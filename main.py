from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from search_engine import SearchEngine
from ingest import ingest_all
from tools import get_tools
from qa_engine import QAEngine
from utils import split_doc

# --- Init Phase --- #
app = FastAPI()

# Initialize Elasticsearch and document stores
search = SearchEngine()
stores = {
    "gdpr": search.get_store("gdpr_docs"),
    "pdp": search.get_store("uupdp_docs"),
    "company": search.get_store("company_docs")
}

# Ingest all available documents
ingest_all(stores)

# Set up tools and QA engine
tools = get_tools(stores, search_cfg={"k": 3, "score_threshold": 0.7})
qa = QAEngine(tools)

# Temp storage for uploaded user content
uploaded_context = {}

# --- Request Models --- #
class QueryRequest(BaseModel):
    query: str
    context: str | None = None

# --- Routes --- #

@app.post("/ask")
def ask(query: QueryRequest):
    context_text = query.context or uploaded_context.get("temp", "")
    answer = qa.answer(query.query)
    return {"answer": answer}


@app.post("/upload")
def upload_doc(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    chunks = split_doc(content)
    joined = "\n\n".join([c.page_content for c in chunks])
    uploaded_context["temp"] = joined
    return {"status": "ok", "context": joined[:5000]}  # Optional: limit response size


@app.post("/reset")
def reset_chat():
    qa.reset_memory()
    uploaded_context.clear()
    return {"status": "reset"}


@app.get("/openapi.json")
def custom_openapi():
    return get_openapi(title="Legal QA", version="1.0.0", routes=app.routes)
