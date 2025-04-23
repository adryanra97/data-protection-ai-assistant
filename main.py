from fastapi import FastAPI, Body
from search_engine import SearchEngine
from ingest import ingest_all
from tools import get_tools
from qa_engine import QAEngine

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

@app.post("/ask")
def ask_question(q: str = Body(..., embed=True)):
    return {"answer": qa.answer(q)}

@app.get("/openapi.json")
def custom_openapi():
    return get_openapi(title="Legal QA", version="1.0.0", routes=app.routes)
