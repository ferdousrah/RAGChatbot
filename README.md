This project demonstrates how to build a real-time chatbot using Django, WebSockets, FAISS, and OpenAI. The chatbot is capable of answering user queries about products and general knowledge from a predefined knowledge base. It combines Retrieval-Augmented Generation (RAG) by using FAISS for fast retrieval of relevant data and OpenAI's GPT model for generating responses.

Features
---------
Real-Time Interaction: Chatbot responds instantly to user queries via WebSocket.
Query Classification: Classifies user queries into product-related or knowledge base-related using OpenAI.
FAISS Search: Efficient similarity search to find relevant products or knowledge base information.
Conversation History: Maintains conversation context using OpenAI's GPT model.
Quick Replies: Predefined buttons for common questions like "Return Policy" or "Discounts".

Technologies Used
-----------------
Django: Web framework for backend.
Django Channels: To handle WebSocket connections for real-time communication.
FAISS: Efficient vector search library to index and search embeddings.
Sentence-Transformers: For embedding product and knowledge base data.
OpenAI GPT: For query classification and generating conversational responses.

Setup and Installation
Follow these steps to set up and run the chatbot locally:

1. Clone the repository
   git clone https://github.com/ferdousrah/RAGChatbot.git
   
   cd rag-chatbot

3. Create and activate a virtual environment
   
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

5. Install dependencies
   
   pip install -r requirements.txt

7. Set up environment variables
   Create a .env file in the project root and add the following variables:

DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=your-openai-api-key
REDIS_HOST=localhost
REDIS_PORT=6379

5. Run Database Migrations
   python manage.py migrate

6. Run the server
   python manage.py runserver

You can now access the chatbot at http://127.0.0.1:8000/chat/

How It Works
--------------
WebSocket Connection: The chatbot uses Django Channels to establish a WebSocket connection with the client. This enables real-time communication, where the user can send messages and receive responses instantly.

Query Classification: Once the user sends a query, it is passed to OpenAI's GPT model, which classifies the query into either product-related or knowledge base-related.

FAISS Search: Based on the classification, the system searches for relevant data using FAISS. If the query is about a product, the product information is fetched from the FAISS index. Similarly, if it's a knowledge base query, the relevant answer is retrieved.

Conversation History: The chatbot maintains a history of the conversation context and uses it to generate more natural and context-aware responses using OpenAI GPT.

Project Structure
-----------------

rag-chatbot/
│
├── chatbot/                  # The chatbot app
│   ├── migrations/           # Database migrations
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py         # WebSocket consumer for chat functionality
│   ├── embeddings.py        # FAISS indexing and embeddings logic
│   ├── models.py            # Database models (Message, Product, KnowledgeBase)
│   ├── routing.py           # WebSocket URL routing
│   ├── views.py             # Views for handling HTTP requests
│   ├── templates/           # Frontend HTML templates
│   └── static/              # Static files (CSS, JS)
│
├── ecommerce_chatbot/       # Main Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py              # ASGI configuration for Channels
│
├── manage.py                # Django command-line utility
└── requirements.txt         # Python dependencies

How to Use
----------
Visit the /chat/ URL on your local server to interact with the chatbot.
You can start typing queries such as:
"Tell me about Mango" (For product queries)
"What is your return policy?" (For knowledge base queries)
The bot will respond based on the context, using both retrieval and generation techniques.

Contributing
------------
Feel free to fork this repository and create pull requests with improvements or bug fixes. If you have any suggestions or issues, please open an issue in the GitHub repository.
