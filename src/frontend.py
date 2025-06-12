import gradio as gr
import requests
from typing import List, Iterator

# Backend URL
BACKEND_URL = "http://localhost:8000/ask"

def chat_with_backend(message: str, history: List[List[str]]) -> Iterator[str]:
    """
    Send message to FastAPI backend and get streaming response
    """
    try:
        # Convert Gradio history format to OpenAI format
        openai_history = []
        for user_msg, assistant_msg in history:
            if user_msg:
                openai_history.append({"role": "user", "content": user_msg})
            if assistant_msg:
                openai_history.append({"role": "assistant", "content": assistant_msg})
        
        # Prepare request payload
        payload = {
            "messages": message,
            "history": openai_history
        }
        
        # Make streaming request
        response = requests.post(
            BACKEND_URL,
            json=payload,
            stream=True,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            yield f"Error: {response.status_code} - {response.text}"
            return
        
        # Stream the response
        full_response = ""
        for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
            if chunk:
                full_response += chunk
                yield full_response
                
    except requests.exceptions.ConnectionError:
        yield "Error: Could not connect to backend. Make sure the FastAPI server is running on localhost:8000"
    except Exception as e:
        yield f"Error: {str(e)}"

# Create Gradio interface

css = """
.gradio-container {
    background-image: url('http://localhost:8000/background.jpeg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

.column {
    height: 90vh;
}

.block, .bubble-wrap {
    background-color: transparent !important;
    border: none !important;
}

.examples {
    margin-bottom: 2rem;
}

footer {
    display: none !important;
}
"""
with gr.Blocks(title="HSBC Well+ Assistant", css=css) as demo:
    gr.HTML(
        '<div style="text-align:center;"><img src="http://localhost:8000/team-logo.png" alt="HSBC Well+ Banner" style="max-width:300px; border-radius:12px; margin-bottom:1.5rem;"></div>'
    )
    chatbot = gr.ChatInterface(
        chat_with_backend,
        examples=[
            "What is HSBC Well+?",
            "How do I join the Well+ program?",
            "What rewards can I earn?",
            "How is my personal data used?",
            "What are the eligibility requirements?",
            "Can I cancel my membership?"
        ],
        
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 