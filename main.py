import gradio as gr
import os
import requests
import json

def hello_world(name):
    return f"Hallo, {name}! Hier sind die Infos die Sie suchen: "


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

demo = gr.Interface(
    fn=generate_chat_response,
    inputs=gr.Textbox(label="Suchbegriff", lines=10),
    outputs=gr.Textbox(label="Infos", lines=30),
    title="Uni Mannheim - IT-Anleitungen",
    description="Hier können Sie die IT-Anleitungen der Universität Mannheim durchsuchen. Bitte geben Sie einen Suchbegriff ein:",
)

demo.launch()
