import os
import sys

from dotenv import load_dotenv

sys.path.append('../../')

from demos.components.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
print(f'Location of RAG DB: {cdb_path}')
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def lookup_in_documentation(query):
    print(f"Searching in documentation: '{query}'")
    results = cdb_store.query_store(query)
    return results[:5]
