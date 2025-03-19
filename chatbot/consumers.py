import json
from channels.generic.websocket import AsyncWebsocketConsumer
import faiss
import numpy as np
import openai
from sentence_transformers import SentenceTransformer
from chatbot.embeddings import create_faiss_index
from chatbot.utils import sentence_model
from django.conf import settings
from asgiref.sync import sync_to_async
from .models import Message
# Set OpenAI API Key
openai.api_key = settings.OPENAI_API_KEY
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
# Create FAISS index at server startup
product_index, products, kb_index, knowledge_base = create_faiss_index()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        # Assign global FAISS variables to instance variables
        self.product_index = product_index
        self.products = products
        self.knowledge_base = knowledge_base
        self.kb_index = kb_index

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        query = text_data_json['message']

        # Use a default sender name for unauthenticated users
        sender = text_data_json.get('sender', 'Anonymous')  # Default to "Anonymous" if no sender is provided

        # Save the user message asynchronously
        await sync_to_async(Message.objects.create)(sender=sender, content=query)

        # Generate bot response (you can call your logic here)
        response = await self.get_response(query)

        # Save the bot response asynchronously
        await sync_to_async(Message.objects.create)(sender='Bot', content=response)
        
        # Send the bot response to the WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": response
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_history = []  # Store conversation history

    async def get_response(self, query):
        try:
            # Step 1: Classify the query
            classification = await self.classify_query_with_openai(query)
            
            # Step 2: Retrieve results based on classification
            if classification == 'product':
                faiss_response = await self.search_faiss(query, 'product')
            elif classification == 'knowledge_base':
                faiss_response = await self.search_faiss(query, 'knowledge_base')
            else:
                faiss_response = "Sorry, I couldn't classify your query."

            # Step 3: Add the query and FAISS response to the conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append(
                {"role": "assistant", "content": faiss_response}
            )

            # Step 4: Generate a conversational response using OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use 'gpt-4' or 'gpt-3.5-turbo'
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a product store assistant. Respond only based on the provided context and avoid adding extra information, assumptions, or disclaimers. "
                            "If the context includes details about a product, provide those details in a helpful and conversational tone. "
                            "If the context does not include the required information, politely say, 'I'm sorry, I couldn't find relevant information in the store.'"
                        ),
                    },
                    *self.conversation_history  # Include the conversation history
                ],
                temperature=0.5,  # Balanced tone
                max_tokens=200
            )
            
            # Extract the assistant's response
            assistant_response = response['choices'][0]['message']['content']
            
            # Step 5: Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            return assistant_response

        except Exception as e:
            print(f"Error during response generation: {e}")
            return "Sorry, I couldn't process your query."




    async def classify_query_with_openai(self, query):
        try:
            print(f"Classifying Query: {query}")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Ensure the correct model name
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a query classifier. Classify user queries into one of the following categories:\n"
                            "- 'product': Use this category if the query is about a product (e.g., 'Tell me about mango', 'What is Mango?').\n"
                            "- 'knowledge_base': Use this category if the query is general knowledge or informational (e.g., 'What is your return policy?').\n"
                            "Respond with either 'product' or 'knowledge_base' only, and do not add any explanation."
                        ),
                    },
                    {"role": "user", "content": f"Classify the following query: {query}"}
                ],
                temperature=0,  # Deterministic output
                max_tokens=10
            )
            
            classification = response['choices'][0]['message']['content'].strip().lower()
            print(f"Classification Result: {classification}")
            
            if classification not in ['product', 'knowledge_base']:
                return "unknown"
            return classification
        
        except Exception as e:
            print(f"Error during classification: {e}")
            return "unknown"



    async def search_faiss(self, query, index_type):
        try:
            query_embedding = np.array([sentence_model.encode(query)]).astype('float32')
            print(f"Query Embedding: {query_embedding}")  # Log query embedding

            index = self.product_index if index_type == 'product' else self.kb_index
            data = self.products if index_type == 'product' else self.knowledge_base

            if index is None or index.ntotal == 0:
                print(f"FAISS index for {index_type} is empty.")  # Log empty index
                return f"No relevant {index_type.replace('_', ' ')} data available."

            # Perform similarity search
            distances, indices = index.search(query_embedding, 3)  # Retrieve top 3 matches
            print(f"FAISS Distances: {distances}, Indices: {indices}")  # Log results

            if np.all(indices == -1):  # No valid matches
                return f"No relevant {index_type.replace('_', ' ')} found for your query."

            return await self.construct_response(indices, index_type, data)

        except Exception as e:
            print(f"Error during FAISS search: {e}")
            return f"Error processing FAISS search: {str(e)}"






    async def construct_response(self, indices, index_type, data):
        responses = []

        for idx in indices[0]:  # Iterate through the FAISS indices
            idx = int(idx)
            if idx < 0 or idx >= len(data):  # Ensure valid index
                continue

            if index_type == 'product':  # Handle product data
                product = data[idx]
                responses.append(
                    f"Product: {product.name}\n"
                    f"Description: {product.description}\n"
                    f"Category: {product.category}\n"
                    f"Price: {product.price} tk\n"
                    f"Stock Quantity: {product.stock_quantity}\n"
                    f"Specifications: {product.specifications}\n"
                )
            elif index_type == 'knowledge_base':  # Handle knowledge base data
                kb_entry = data[idx]
                responses.append(
                    f"Knowledge Base:\n"
                    f"Question: {kb_entry.question}\n"
                    f"Answer: {kb_entry.answer}\n"
                )

        if not responses:
            return "I'm sorry, I couldn't find any relevant matches."

        return "\n".join(responses)




