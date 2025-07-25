import gradio as gr
import requests

API_URL_ASK = "http://localhost:8000/ask"
API_URL_RESET = "http://localhost:8000/reset"
API_URL_UPLOAD = "http://localhost:8000/upload"

# Simpan context global
context_state = {"context": None}

# Penjelasan aplikasi
DESCRIPTION = (
    "![Logo](logo.png)\n\n"
    "## Legal Intelligence Chatbot\n"
    "Sebuah chatbot canggih untuk menjawab pertanyaan seputar **GDPR, UU PDP, dan Kebijakan Perusahaan**.\n\n"
    "Ditenagai oleh **Multi-Agent LLM Technology**, OpenAI, Elasticsearch & Tavily.\n"
)

def chat_with_bot(message, history):
    try:
        payload = {"query": message}
        if context_state["context"]:
            payload["context"] = context_state["context"]

        response = requests.post(API_URL_ASK, json=payload)
        answer = response.json().get("answer", "Maaf, tidak ada jawaban ditemukan.")
    except Exception as e:
        answer = f"Error: {str(e)}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})
    return "", history

def reset_memory():
    try:
        requests.post(API_URL_RESET)
    except:
        pass
    context_state["context"] = None
    return []

def upload_file(file):
    if not file:
        return "Tidak ada file dipilih"
    try:
        with open(file.name, "rb") as f:
            response = requests.post(API_URL_UPLOAD, files={"file": f})
        if response.status_code == 200:
            context_state["context"] = response.json().get("context")
            return "Dokumen berhasil diunggah. Silakan bertanya berdasarkan isi file."
        else:
            return f"Gagal mengunggah: {response.status_code}"
    except Exception as e:
        return f"Error saat upload: {str(e)}"

with gr.Blocks(title="Legal Chatbot") as demo:
    gr.Markdown(DESCRIPTION)

    chatbot = gr.Chatbot(label="Percakapan", type="messages")

    with gr.Row():
        msg = gr.Textbox(placeholder="Tulis pertanyaan hukum Anda di sini...", show_label=False, scale=8)
        clear_btn = gr.Button("Reset Chat", scale=2)

    with gr.Row():
        upload = gr.File(label="Upload Dokumen", file_types=[".txt", ".csv"])
        status = gr.Textbox(label="Status Upload", interactive=False)

    msg.submit(chat_with_bot, [msg, chatbot], [msg, chatbot])
    clear_btn.click(fn=reset_memory, inputs=[], outputs=[chatbot])
    upload.change(fn=upload_file, inputs=upload, outputs=status)

    gr.Markdown("<center><small>Dibangun dengan LangChain, OpenAI, Elasticsearch, Tavily</small></center>")

demo.launch()
