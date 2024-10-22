import os
import sys

from dotenv import load_dotenv

from demos.components.chroma_document_store import ChromaDocumentStore

sys.path.append('../../')

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def lookup_in_documentation(query):
    print(f"Searching in company docs: '{query}'")
    results = cdb_store.query_store(query)
    return results[:5]