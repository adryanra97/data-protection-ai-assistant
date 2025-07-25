from langchain_core.documents import Document
from typing import List

def split_doc(text: str) -> List[Document]:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    max_chunk_size = 1500
    for para in paragraphs:
        para = para.strip()
        if len(current_chunk) + len(para) <= max_chunk_size:
            current_chunk += "\n\n" + para
        else:
            if current_chunk.strip():
                chunks.append(Document(page_content=current_chunk.strip()))
            current_chunk = para
    if current_chunk.strip():
        chunks.append(Document(page_content=current_chunk.strip()))
    return chunks
