import gradio as gr
import requests

API_URL_ASK = "http://localhost:8000/ask"
API_URL_RESET = "http://localhost:8000/reset"
API_URL_UPLOAD = "http://localhost:8000/upload"

DESCRIPTION =   """
<style>
#chatbot-area .message.user {background-color: #e7eff6; color: #003366; border-radius: 10px; padding: 8px; margin: 6px;}
#chatbot-area .message.bot {background-color: #f2f4f8; border-left: 4px solid #003366; border-radius: 10px; padding: 8px; margin: 6px;}
#chatbot-area .message {font-family: 'Segoe UI', sans-serif; font-size: 14px;}
#logo {text-align: center; margin-bottom: 10px;}
</style>

<div id='logo'>
    <img src='file/logo.png' alt='Logo' style='height: 80px;'>
</div>

<h2 style='color:#003366;'>Legal Intelligence Chatbot</h2>
<p>
Sebuah chatbot canggih untuk menjawab pertanyaan seputar <strong>GDPR, UU PDP, dan Kebijakan Perusahaan</strong>.<br>
Ditenagai oleh <strong>Multi-Agent LLM Technology</strong>, OpenAI, Elasticsearch & Tavily.
</p>
"""

def chat_with_bot(message, history, context):
    try:
        payload = {"query": message}
        if context:
            payload["context"] = context
        response = requests.post(API_URL_ASK, json=payload)
        response.raise_for_status()
        answer = response.json().get("answer", "Maaf, tidak ada jawaban ditemukan.")
    except Exception as e:
        answer = f"Error: {str(e)}"
    history.append((message, answer))
    return "", history, context

def reset_memory():
    try:
        requests.post(API_URL_RESET)
    except:
        pass
    return [], None

def upload_file(file):
    if not file:
        return "Tidak ada file dipilih", None
    try:
        with open(file.name, "rb") as f:
            response = requests.post(API_URL_UPLOAD, files={"file": f})
        if response.status_code == 200:
            return "Dokumen berhasil diunggah. Silakan bertanya berdasarkan isi file.", response.json().get("context")
        else:
            return f"Gagal mengunggah: {response.status_code}", None
    except Exception as e:
        return f"Error saat upload: {str(e)}", None

with gr.Blocks(css="#chatbot-area .message { max-width: 80%; }") as demo:
    state = gr.State({"context": None})
    gr.Markdown(DESCRIPTION, unsafe_allow_html=True)

    with gr.Box(elem_id="chatbot-area"):
        chatbot = gr.Chatbot(label="Percakapan")

    with gr.Row():
        msg = gr.Textbox(placeholder="Tulis pertanyaan hukum Anda di sini...", show_label=False, scale=8)
        clear_btn = gr.Button("Reset Chat", scale=2)

    with gr.Row():
        upload = gr.File(label="Upload Dokumen", file_types=[".txt", ".csv"])
        status = gr.Textbox(label="Status Upload", interactive=False)

    msg.submit(chat_with_bot, [msg, chatbot, state], [msg, chatbot, state])
    clear_btn.click(fn=reset_memory, inputs=[], outputs=[chatbot, state])
    upload.change(fn=upload_file, inputs=upload, outputs=[status, state])

    gr.Markdown("<center><small>Dibangun dengan LangChain, OpenAI, Elasticsearch, Tavily</small></center>", unsafe_allow_html=True)

if __name__ == "__main__":
    demo.launch()
