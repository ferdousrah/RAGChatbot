# chatbot/embeddings.py
import openai
from sentence_transformers import SentenceTransformer
from .models import Product, KnowledgeBase
import faiss
import numpy as np
import psycopg2
from django.conf import settings

# Initialize OpenAI API and Sentence-Transformer
openai.api_key = settings.OPENAI_API_KEY
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')  # You can use other models as well

# Embedding for Product Models
def embed_product_data():
    products = Product.objects.all()
    product_embeddings = []

    for product in products:
        text = f"Name: {product.name}, Description: {product.description}, Category: {product.category}"
        embedding = sentence_model.encode(text).tolist()
        product_embeddings.append(embedding)

    return product_embeddings, products

# Embedding for Knowledge Base Models
def embed_knowledgebase_data():
    knowledge_base = KnowledgeBase.objects.all()
    kb_embeddings = []

    for entry in knowledge_base:
        text = f"Q: {entry.question}, A: {entry.answer}"
        embedding = sentence_model.encode(text).tolist()
        kb_embeddings.append(embedding)

    return kb_embeddings, knowledge_base

# Store the embeddings using FAISS
def create_faiss_index():
    product_embeddings, products = embed_product_data()
    kb_embeddings, knowledge_base = embed_knowledgebase_data()

    print(f"Number of Product Embeddings: {len(product_embeddings)}")
    print(f"Number of Knowledge Base Embeddings: {len(kb_embeddings)}")

    if not product_embeddings and not kb_embeddings:
        print("Error: No data found for FAISS index creation.")
        return None, [], None, []

    product_index = faiss.IndexFlatL2(len(product_embeddings[0])) if product_embeddings else None
    kb_index = faiss.IndexFlatL2(len(kb_embeddings[0])) if kb_embeddings else None

    if product_index:
        product_index.add(np.array(product_embeddings).astype('float32'))
    if kb_index:
        kb_index.add(np.array(kb_embeddings).astype('float32'))

    print(f"Product Index Size: {product_index.ntotal if product_index else 0}")
    print(f"Knowledge Base Index Size: {kb_index.ntotal if kb_index else 0}")

    return product_index, products, kb_index, knowledge_base



