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
    "history": f"{API_BASE_URL}/conversation/history",
    "documents_upload": f"{API_BASE_URL}/documents/upload",
    "documents_list": f"{API_BASE_URL}/documents",
    "documents_status": f"{API_BASE_URL}/documents",  # will append /{id}/status
    "documents_delete": f"{API_BASE_URL}/documents"   # will append /{id}
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
            
            return f"{message}\nCreated {chunks} chunks\nPreview: {preview[:200]}..."
        
        else:
            error_msg = f"Upload failed with status {response.status_code}"
            logger.error(f"Upload failed: {response.text}")
            return f"{error_msg}"
    
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return f"Upload error: {str(e)}"


def upload_document_new(file, title: str = "", description: str = "", category: str = "user_upload") -> str:
    """
    Upload and process a document with enhanced metadata.
    
    Args:
        file: Uploaded file object
        title: Custom title for the document
        description: Description of the document
        category: Document category
        
    Returns:
        str: Upload status message
    """
    if not file:
        return "No file selected"
    
    try:
        # Prepare form data
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f)}
            data = {
                "title": title or file.name,
                "description": description,
                "category": category
            }
            
            response = requests.post(
                API_ENDPOINTS["documents_upload"],
                files=files,
                data=data,
                timeout=60  # Longer timeout for document processing
            )
        
        if response.status_code == 200:
            result = response.json()
            doc_info = result.get("document", {})
            
            message = f"Document uploaded successfully!\n"
            message += f"Title: {doc_info.get('title', 'Unknown')}\n"
            message += f"ID: {doc_info.get('id', 'Unknown')}\n"
            message += f"Chunks: {doc_info.get('chunk_count', 0)}\n"
            message += f"Category: {doc_info.get('category', 'Unknown')}\n"
            message += f"Status: {'Active' if doc_info.get('is_active', False) else 'Inactive'}\n"

            return message
        
        else:
            error_msg = f"Upload failed with status {response.status_code}"
            logger.error(f"Upload failed: {response.text}")
            return error_msg
    
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return f"Upload error: {str(e)}"


def list_documents(category_filter: str = "") -> str:
    """
    List all uploaded documents.
    
    Args:
        category_filter: Filter by category (optional)
        
    Returns:
        str: Formatted list of documents
    """
    try:
        params = {"category": category_filter} if category_filter else {}
        response = requests.get(API_ENDPOINTS["documents_list"], params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            
            if not documents:
                return "No documents found."

            result = f"Documents ({len(documents)} total)\n\n"

            for doc in documents:
                status_icon = "🟢" if doc.get("is_active", False) else "🔴"
                result += f"{status_icon} **{doc.get('title', 'Untitled')}**\n"
                result += f"   ID: `{doc.get('id', 'Unknown')}`\n"
                result += f"   Category: {doc.get('category', 'Unknown')}\n"
                result += f"   Chunks: {doc.get('chunk_count', 0)}\n"
                result += f"   Uploaded: {doc.get('created_at', 'Unknown')}\n"
                if doc.get('description'):
                    result += f"   Description: {doc.get('description')}\n"
                result += "\n"
            
            return result
        
        else:
            return f"Failed to list documents (Status: {response.status_code})"

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return f"Error listing documents: {str(e)}"


def toggle_document_status(document_id: str, activate: bool) -> str:
    """
    Toggle document activation status.
    
    Args:
        document_id: ID of the document
        activate: True to activate, False to deactivate
        
    Returns:
        str: Status update message
    """
    if not document_id.strip():
        return "Please provide a document ID"
    
    try:
        url = f"{API_ENDPOINTS['documents_status']}/{document_id}/status"
        data = {"is_active": activate}
        
        response = requests.put(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            status = "activated" if activate else "deactivated"
            return f"Document successfully {status}!\nID: {document_id}"
        
        elif response.status_code == 404:
            return f"Document not found: {document_id}"
        
        else:
            return f"Failed to update document status (Status: {response.status_code})"

    except Exception as e:
        logger.error(f"Error updating document status: {e}")
        return f"Error updating document status: {str(e)}"


def delete_document(document_id: str) -> str:
    """
    Delete a document from the knowledge base.
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        str: Deletion status message
    """
    if not document_id.strip():
        return "Please provide a document ID"
    
    try:
        url = f"{API_ENDPOINTS['documents_delete']}/{document_id}"
        response = requests.delete(url, timeout=10)
        
        if response.status_code == 200:
            return f"Document deleted successfully!\nID: {document_id}"

        elif response.status_code == 404:
            return f"Document not found: {document_id}"

        else:
            return f"Failed to delete document (Status: {response.status_code})"

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return f"Error deleting document: {str(e)}"


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
            max-width: 1200px !important;
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
        
        # Main interface with tabs
        with gr.Tabs():
            # Chat Tab
            with gr.TabItem("Chat Assistant"):
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
                    
                    # Sidebar for quick document upload
                    with gr.Column(scale=1):
                        gr.Markdown("### Quick Document Upload")
                        gr.Markdown("Upload documents for immediate use in conversation.")
                        
                        file_upload_quick = gr.File(
                            label="Select Document",
                            file_types=[".txt", ".csv", ".md", ".pdf"],
                            elem_classes=["upload-area"]
                        )
                        
                        upload_status_quick = gr.Textbox(
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
            
            # Document Management Tab
            with gr.TabItem("Document Management"):
                gr.Markdown("## Document Management")
                gr.Markdown("Upload, manage, and control documents in your knowledge base. Documents can be activated/deactivated for use in RAG queries.")
                
                with gr.Row():
                    # Upload Section
                    with gr.Column(scale=1):
                        gr.Markdown("### Upload New Document")
                        
                        file_upload_new = gr.File(
                            label="Select Document",
                            file_types=[".txt", ".csv", ".xlsx", ".pdf"],
                            elem_classes=["upload-area"]
                        )
                        
                        doc_title = gr.Textbox(
                            label="Document Title (optional)",
                            placeholder="Enter a custom title for this document"
                        )
                        
                        doc_description = gr.Textbox(
                            label="Description (optional)",
                            placeholder="Describe the content or purpose of this document",
                            lines=3
                        )
                        
                        doc_category = gr.Dropdown(
                            label="Category",
                            choices=["user_upload", "gdpr", "pdp", "company_policy", "legal_doc"],
                            value="user_upload"
                        )
                        
                        upload_btn = gr.Button("Upload Document", variant="primary")
                        
                        upload_result = gr.Textbox(
                            label="Upload Result",
                            interactive=False,
                            lines=6
                        )
                    
                    # Document List Section
                    with gr.Column(scale=1):
                        gr.Markdown("### Document Library")
                        
                        category_filter = gr.Dropdown(
                            label="Filter by Category",
                            choices=["", "user_upload", "gdpr", "pdp", "company_policy", "legal_doc"],
                            value="",
                            allow_custom_value=True
                        )
                        
                        list_btn = gr.Button("Refresh Document List", variant="secondary")
                        
                        document_list = gr.Textbox(
                            label="Documents",
                            interactive=False,
                            lines=10,
                            value=list_documents()
                        )
                        
                        gr.Markdown("### Document Controls")
                        
                        doc_id_input = gr.Textbox(
                            label="Document ID",
                            placeholder="Enter document ID for operations"
                        )
                        
                        with gr.Row():
                            activate_btn = gr.Button("Activate", variant="primary")
                            deactivate_btn = gr.Button("Deactivate", variant="secondary")
                            delete_btn = gr.Button("Delete", variant="stop")
                        
                        control_result = gr.Textbox(
                            label="Operation Result",
                            interactive=False,
                            lines=3
                        )
        
        # Event handlers for Chat Tab
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
        
        file_upload_quick.change(
            fn=upload_document,
            inputs=[file_upload_quick],
            outputs=[upload_status_quick]
        )
        
        # Event handlers for Document Management Tab
        upload_btn.click(
            fn=upload_document_new,
            inputs=[file_upload_new, doc_title, doc_description, doc_category],
            outputs=[upload_result]
        )
        
        list_btn.click(
            fn=list_documents,
            inputs=[category_filter],
            outputs=[document_list]
        )
        
        activate_btn.click(
            fn=lambda doc_id: toggle_document_status(doc_id, True),
            inputs=[doc_id_input],
            outputs=[control_result]
        )
        
        deactivate_btn.click(
            fn=lambda doc_id: toggle_document_status(doc_id, False),
            inputs=[doc_id_input],
            outputs=[control_result]
        )
        
        delete_btn.click(
            fn=delete_document,
            inputs=[doc_id_input],
            outputs=[control_result]
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
