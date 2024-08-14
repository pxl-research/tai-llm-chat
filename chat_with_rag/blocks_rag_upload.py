import os
import sys

import chromadb
import gradio as gr
from dotenv import load_dotenv

sys.path.append('../')

from demos.rag.fn_chromadb import add_pdf_to_db

load_dotenv()

# cdb_client = chromadb.Client()  # in memory
cdb_path = os.getenv("CHROMA_LOCATION")
cdb_client = chromadb.PersistentClient(path=cdb_path)  # on disk


# https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
def cleanup_filename(full_file_path):
    cleaned_name = os.path.basename(full_file_path)  # remove path
    cleaned_name = os.path.splitext(cleaned_name)[0]  # remove extension
    cleaned_name = cleaned_name.lower()  # lowercase
    cleaned_name = cleaned_name.replace(".", "_")  # no periods
    return cleaned_name[:60]  # crop it


def on_file_uploaded(file_path, progress=gr.Progress()):
    collection_name = cleanup_filename(file_path)
    add_pdf_to_db(cdb_client, collection_name, file_path, progress)
    names = list_collections()
    return [None, names]


def list_collections():
    collections_list = cdb_client.list_collections()
    names = []
    for collection in collections_list:
        names.append([collection.name])
    return names