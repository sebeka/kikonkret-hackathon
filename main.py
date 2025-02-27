import gradio as gr
import os
import requests
import json

import markdown
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings

import faiss
import numpy as np

def hello_world(name):
    return f"Hallo, {name}! Hier sind die Infos die Sie suchen: "

def load_and_split_markdown(directory_path):
    texts = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
                html = markdown.markdown(file.read())
                # Optionally, use BeautifulSoup to extract text from HTML
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                # Split text into chunks
                splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
                chunks = splitter.split_text(text)
                texts.extend(chunks)
    return texts

markdown_texts = load_and_split_markdown('markdown_text')

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
document_embeddings = embeddings.embed_documents(markdown_texts)

dimension = len(document_embeddings[0])  # Typically 768 for many embedding models
index = faiss.IndexFlatL2(dimension)  # Using L2 distance
index.add(np.array(document_embeddings).astype('float32'))

def retrieve(query, top_k=5):
    query_embedding = embeddings.embed_query(query)
    D, I = index.search(np.array([query_embedding]).astype('float32'), top_k)
    retrieved_texts = [markdown_texts[i] for i in I[0]]
    return retrieved_texts

def generate_chat_response(user_message):
    url = "https://chat-ai.academiccloud.de/v1/chat/completions"
    api_key = os.getenv("API_KEY")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0
    }

    # Sending the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # If the request was successful, return the reply from the model
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', 'No response content found.')
    else:
        # If there was an error, return the status code and error message
        return f"Error: {response.status_code}, {response.text}"

def generate_response(user_query):
    retrieved_docs = retrieve(user_query, top_k=5)
    context = "\n\n".join(retrieved_docs)
    combined_prompt = f"Context:\n{context}\n\nUser Query:\n{user_query}\n\nAnswer:"
    response = generate_chat_response(combined_prompt)
    return response

def rag_interface(user_input):
    response = generate_response(user_input)
    return response

demo = gr.Interface(
    fn=rag_interface,
    inputs=gr.Textbox(label="Suchbegriff", lines=10),
    outputs=gr.Textbox(label="Infos", lines=30),
    title="Uni Mannheim - IT-Anleitungen",
    description="Hier können Sie die IT-Anleitungen der Universität Mannheim durchsuchen. Bitte geben Sie einen Suchbegriff ein:",
)

demo.launch()
