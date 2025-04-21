from llama_index.core import SimpleDirectoryReader

def summarize_document(dir) -> str:
    return SimpleDirectoryReader(dir).load_data()
