"""
Gradio Web Interface for Data Protection AI Assistant

This module provides a user-friendly web interface using Gradio for
interacting with the Data Protection AI Assistant.

Author: Adryan R A
"""

import logging
import requests
from typing import List, Tuple, Optional
import gradio as gr

from ..core.config import settings
from ..utils.logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# API endpoints configuration
API_BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}"
API_ENDPOINTS = {
    "ask": f"{API_BASE_URL}/ask",
    "reset": f"{API_BASE_URL}/reset",
    "upload": f"{API_BASE_URL}/upload",
    "health": f"{API_BASE_URL}/health",
    "history": f"{API_BASE_URL}/conversation/history"
}

# Global state for context management
app_state = {
    "context": None,
    "conversation_history": [],
    "api_status": "Unknown"
}


class UIError(Exception):
    """Custom exception for UI-related errors."""
    pass


def check_api_health() -> str:
    """
    Check the health status of the API backend.
    
    Returns:
        str: Health status message
    """
    try:
        response = requests.get(API_ENDPOINTS["health"], timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            app_state["api_status"] = status
            return f"API Status: {status.upper()}"
        else:
            app_state["api_status"] = "error"
            return f"API Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        app_state["api_status"] = "unavailable"
        logger.error(f"API health check failed: {e}")
        return "API Status: UNAVAILABLE"


def chat_with_assistant(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """
    Send a message to the AI assistant and get a response.
    
    Args:
        message (str): User's message
        history (List[List[str]]): Conversation history
        
    Returns:
        Tuple[str, List[List[str]]]: Empty message input and updated history
    """
    if not message or not message.strip():
        return "", history
    
    try:
        # Prepare request payload
        payload = {"query": message.strip()}
        if app_state["context"]:
            payload["context"] = app_state["context"]
        
        # Send request to API
        response = requests.post(
            API_ENDPOINTS["ask"],
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "I apologize, but I couldn't generate a response.")
            processing_time = data.get("processing_time", 0)
            
            # Add processing time info if available
            if processing_time > 0:
                answer += f"\n\n*Response generated in {processing_time:.2f} seconds*"
            
        else:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            answer = f"I apologize, but I encountered an error (Status: {response.status_code}). Please try again."
    
    except requests.exceptions.Timeout:
        answer = "The request timed out. Please try again with a shorter or simpler question."
        logger.error("API request timed out")
    
    except requests.exceptions.RequestException as e:
        answer = f"I couldn't connect to the AI service. Please check your connection and try again."
        logger.error(f"API request failed: {e}")
    
    except Exception as e:
        answer = f"An unexpected error occurred: {str(e)}"
        logger.error(f"Unexpected error in chat: {e}")
    
    # Update history
    history.append([message, answer])
    app_state["conversation_history"] = history
    
    return "", history


def reset_conversation() -> Tuple[List, str]:
    """
    Reset the conversation history and memory.
    
    Returns:
        Tuple[List, str]: Empty history and status message
    """
    try:
        # Reset API memory
        response = requests.post(API_ENDPOINTS["reset"], timeout=10)
        
        if response.status_code == 200:
            status_message = "Conversation reset successfully!"
        else:
            status_message = f"Reset request failed (Status: {response.status_code})"
            
    except requests.exceptions.RequestException as e:
        status_message = "Could not reset conversation - API unavailable"
        logger.error(f"Reset request failed: {e}")
    
    # Clear local state
    app_state["context"] = None
    app_state["conversation_history"] = []
    
    return [], status_message


def upload_document(file) -> str:
    """
    Upload and process a document for context.
    
    Args:
        file: Uploaded file object
        
    Returns:
        str: Upload status message
    """
    if not file:
        return "No file selected"
    
    try:
        # Read file content
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f, "text/plain")}
            
            response = requests.post(
                API_ENDPOINTS["upload"],
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            message = data.get("message", "Upload completed")
            chunks = data.get("chunks_created", 0)
            preview = data.get("preview", "")
            
            # Store context locally
            if preview:
                app_state["context"] = preview
            
            return f"{message}\n📄 Created {chunks} chunks\n📝 Preview: {preview[:200]}..."
        
        else:
            error_msg = f"Upload failed with status {response.status_code}"
            logger.error(f"Upload failed: {response.text}")
            return f"{error_msg}"
    
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return f"Upload error: {str(e)}"


def load_conversation_history() -> List[List[str]]:
    """
    Load conversation history from the API.
    
    Returns:
        List[List[str]]: Conversation history
    """
    try:
        response = requests.get(API_ENDPOINTS["history"], timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            history_data = data.get("history", [])
            
            # Convert to gradio format
            history = []
            for exchange in history_data:
                question = exchange.get("question", "")
                answer = exchange.get("answer", "")
                history.append([question, answer])
            
            app_state["conversation_history"] = history
            return history
        
    except Exception as e:
        logger.error(f"Failed to load conversation history: {e}")
    
    return []


def create_interface() -> gr.Blocks:
    """
    Create and configure the Gradio interface.
    
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    # Application description
    description = """
    # Data Protection AI Assistant
    
    An advanced AI-powered legal assistant specializing in data protection and privacy law. 
    Get expert guidance on **GDPR**, **Indonesia's UU PDP**, and **company data protection policies**.
    
    ## Features
    - **Multi-Agent Intelligence**: Specialized agents for different legal domains
    - **Document Context**: Upload documents for personalized advice
    - **Real-time Search**: Access to current legal information
    - **Conversation Memory**: Maintains context throughout your session
    
    ## How to Use
    1. Type your legal question in the chat box below
    2. Optionally upload relevant documents for additional context
    3. Get comprehensive, source-backed legal guidance
    4. Continue the conversation for follow-up questions
    
    ---
    """
    
    with gr.Blocks(
        title="Data Protection AI Assistant",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1000px !important;
        }
        .chat-message {
            font-size: 14px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        """
    ) as interface:
        
        # Header
        gr.Markdown(description)
        
        # API Status
        with gr.Row():
            api_status = gr.Textbox(
                value=check_api_health(),
                label="System Status",
                interactive=False,
                scale=2
            )
            refresh_btn = gr.Button("Refresh Status", scale=1)
        
        # Main chat interface
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Legal Assistant Chat",
                    height=500,
                    show_label=True,
                    value=load_conversation_history(),
                    elem_classes=["chat-message"]
                )
                
                # Message input
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask your legal question here... (e.g., 'What are the GDPR data subject rights?')",
                        label="Your Question",
                        scale=4,
                        lines=2
                    )
                    send_btn = gr.Button("Send", scale=1, variant="primary")
                
                # Control buttons
                with gr.Row():
                    clear_btn = gr.Button("Reset Chat", variant="secondary")
                    status_display = gr.Textbox(
                        label="Status",
                        interactive=False,
                        visible=False
                    )
            
            # Sidebar for document upload and settings
            with gr.Column(scale=1):
                gr.Markdown("### Document Upload")
                gr.Markdown("Upload legal documents to provide additional context for your questions.")
                
                file_upload = gr.File(
                    label="Select Document",
                    file_types=[".txt", ".csv", ".md", ".pdf"],
                    elem_classes=["upload-area"]
                )
                
                upload_status = gr.Textbox(
                    label="Upload Status",
                    interactive=False,
                    lines=3
                )
                
                gr.Markdown("### Tips")
                gr.Markdown("""
                - Be specific in your questions
                - Mention relevant jurisdictions (EU, Indonesia, etc.)
                - Upload relevant documents for better context
                - Use follow-up questions for clarification
                """)
                
                gr.Markdown("### Example Questions")
                gr.Markdown("""
                - "What are the penalties for GDPR violations?"
                - "How does UU PDP differ from GDPR?"
                - "What is required for valid consent?"
                - "How should data breaches be reported?"
                """)
        
        # Event handlers
        send_btn.click(
            fn=chat_with_assistant,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        msg_input.submit(
            fn=chat_with_assistant,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        clear_btn.click(
            fn=reset_conversation,
            outputs=[chatbot, status_display]
        )
        
        file_upload.change(
            fn=upload_document,
            inputs=[file_upload],
            outputs=[upload_status]
        )
        
        refresh_btn.click(
            fn=check_api_health,
            outputs=[api_status]
        )
        
        # Footer
        gr.Markdown("""
        ---
        <center>
        <small>
        **Data Protection AI Assistant v1.0.0** | 
        Built with LangChain, OpenAI, Elasticsearch & Gradio | 
        For educational purposes - consult legal professionals for specific advice
        </small>
        </center>
        """)
    
    return interface


def launch_interface(
    server_name: str = "0.0.0.0",
    server_port: int = 7860,
    share: bool = False,
    debug: bool = False
) -> None:
    """
    Launch the Gradio web interface.
    
    Args:
        server_name (str): Server hostname
        server_port (int): Server port
        share (bool): Whether to create a public link
        debug (bool): Enable debug mode
    """
    try:
        logger.info("Starting Gradio web interface...")
        
        interface = create_interface()
        
        interface.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            debug=debug,
            show_error=True,
            show_tips=True,
            enable_queue=True
        )
        
    except Exception as e:
        logger.error(f"Failed to launch interface: {e}")
        raise UIError(f"Interface launch failed: {e}")


if __name__ == "__main__":
    # Launch with default settings
    launch_interface(
        debug=settings.DEBUG,
        share=False  # Set to True to create public link
    )
