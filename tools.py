import requests
from langchain.tools import Tool
from config import settings

def retrieve_chunks(store, query: str, search_cfg: dict) -> list[str]:
    docs = store.as_retriever(search_kwargs=search_cfg).get_relevant_documents(query)
    return [d.page_content for d in docs]

def get_tools(stores: dict, search_cfg: dict) -> dict:
    return {
        "gdpr": Tool(
            name="AskGDPR",
            description="Return GDPR chunks verbatim",
            func=lambda q: "\n\n".join(retrieve_chunks(stores['gdpr'], q, search_cfg)) or None
        ),
        "pdp": Tool(
            name="AskPDP",
            description="Return UU PDP chunks verbatim",
            func=lambda q: "\n\n".join(retrieve_chunks(stores['pdp'], q, search_cfg)) or None
        ),
        "company": Tool(
            name="AskCompany",
            description="Return Company Policy chunks verbatim",
            func=lambda q: "\n\n".join(retrieve_chunks(stores['company'], q, search_cfg)) or None
        ),
        "tavily": Tool(
            name="AskTavily",
            description="Pencarian fallback via Tavily",
            func=lambda query: (
                (lambda r: r.json().get("results", [{}])[0].get("content", f"Error Tavily: {r.status_code} - {r.text}")
                 if r.status_code == 200 else f"Fail Tavily: {r.status_code} - {r.text}")
                (requests.post(
                    settings.TAVILY_API_URL,
                    headers={"Authorization": f"Bearer {settings.TAVILY_API_KEY}"},
                    json={"query": query, "search_depth": "advanced", "max_results": 3}
                ))
            )
        )
    }
