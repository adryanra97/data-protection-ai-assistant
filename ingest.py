import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from typing import List
from utils import split_doc

def ingest_all(stores: dict):
    for label, (folder, store) in {
        "gdpr": ("data/gdpr/", stores['gdpr']),
        "pdp": ("data/uupdp/", stores['pdp']),
        "company": ("data/company/", stores['company'])
    }.items():
        for fp in glob.glob(os.path.join(folder, "*.csv")):
            for doc in TextLoader(fp).load():
                for chunk in split_doc(doc.page_content):
                    store.add_documents([chunk])
