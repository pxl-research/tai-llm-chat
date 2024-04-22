import time

from rag_demo.pdf_utils import (pdf_to_text, pages_to_chunks)


def add_pdf_to_db(cdb_client, collection_name, file_path):
    start_time = time.time()  # estimate about 220ms per chunk

    page_list = pdf_to_text(file_path)
    print(f"Extracted {len(page_list)} pages from '{file_path}'")

    chunks, chunk_ids, meta_infos = pages_to_chunks(page_list, collection_name)
    print(f"Split {len(page_list)} pages into {len(chunk_ids)} chunks")

    # https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
    new_collection = cdb_client.create_collection(collection_name)
    new_collection.add(
        documents=chunks,
        ids=chunk_ids,
        metadatas=meta_infos
    )
    duration = (time.time() - start_time)  # convert to ms
    print(f"Added {len(chunk_ids)} chunks to chroma db ({round(duration)} sec)")


def query_all_documents(cdb_client, query):
    collections = cdb_client.list_collections()
    all_results = []
    for collection in collections:
        print(f"Looking up in '{collection.name}'")
        cdb_client.get_collection(collection.name)
        result = collection.query(
            query_texts=[query],
            n_results=5,
        )
        repacked = repack_results(result)
        all_results = all_results + repacked

    # sort results by distance
    # TODO: grab surrounding chunks

    return sorted(all_results, key=lambda r: r['distances'])


def repack_results(result):
    fields = ['distances', 'metadatas', 'embeddings', 'documents', 'uris', 'data']
    length = len(result['ids'][0])  # ids are always returned
    repacked = []
    for r in range(length):
        repacked_result = {'ids': result['ids'][0][r]}
        for field in fields:
            if result[field] is not None:
                repacked_result[field] = result[field][0][r]
        repacked.append(repacked_result)
    return repacked
