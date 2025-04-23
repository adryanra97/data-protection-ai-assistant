from fastapi import FastAPI, Body, UploadFile, File
from search_engine import SearchEngine
from ingest import ingest_all
from tools import get_tools
from qa_engine import QAEngine
from fastapi.responses import JSONResponse
from ingest import split_doc

app = FastAPI()

# Init
search = SearchEngine()
stores = {
    "gdpr": search.get_store("gdpr_docs"),
    "pdp": search.get_store("uupdp_docs"),
    "company": search.get_store("company_docs")
}
ingest_all(stores)
tools = get_tools(stores, search_cfg={"k": 3, "score_threshold": 0.7})
qa = QAEngine(tools)

uploaded_context = {}  

@app.post("/ask")
def ask(query: QueryRequest):
    context_text = query.context or uploaded_context.get("temp", "")
    return {"answer": final_answer(query.query, context_text)}

@app.get("/openapi.json")
def custom_openapi():
    return get_openapi(title="Legal QA", version="1.0.0", routes=app.routes)

@app.post("/upload")
def upload_doc(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    chunks = split_doc(content)
    joined = "\n\n".join([c.page_content for c in chunks])
    uploaded_context["temp"] = joined
    return {"status": "ok", "context": joined[:5000]}  # limit panjang

@app.post("/reset")
def reset_chat():
    reset_memory()
    uploaded_context.clear()
    return {"status": "reset"}
