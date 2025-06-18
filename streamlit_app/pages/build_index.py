import streamlit as st
import ollama
import os
import sys
import time
import logging
import json
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    SimpleDirectoryReader,
    load_index_from_storage
)
from llama_index.core.settings import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.web import SimpleWebPageReader

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ["OLLAMA_HOST"] = OLLAMA_BASE_URL
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

st.set_page_config(page_title="Jetson Copilot - Build Index", page_icon="🛠️")

INDEX_DIR = "Indexes"
DOC_ROOT = "Documents"
os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(DOC_ROOT, exist_ok=True)

def is_embedding_model(model_name):
    return (
        "embed" in model_name.lower() or
        "embedding" in model_name.lower() or
        "mxbai" in model_name.lower() or
        "bge" in model_name.lower()
    )

def write_index_metadata(index_path, embedding_model_name):
    meta_path = os.path.join(index_path, "metadata.json")
    metadata = {
        "embedding_model": embedding_model_name,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

def read_index_metadata(index_path):
    meta_path = os.path.join(index_path, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            return json.load(f)
    else:
        return {}

# Models from Ollama
try:
    ollama_models = ollama.list().get("models", [])
    all_models = [m.get("name") or m.get("model") for m in ollama_models]
except Exception as e:
    st.error(f"Failed to query Ollama host: {e}")
    all_models = []

embedding_models = [m for m in all_models if is_embedding_model(m)]
default_embedding = (
    "mxbai-embed-large:latest"
    if "mxbai-embed-large:latest" in embedding_models
    else (embedding_models[0] if embedding_models else "")
)

st.title("🛠️ Build / Extend RAG Index")

st.info(
    "ℹ️ **This system is best suited for indexing mostly unique documents (PDFs, Word, Markdown, text, etc).** "
    "It's not optimized for aggregating massive log files or extremely repetitive content. "
    "Contact your system admin if you need high-volume or aggregation support."
)

def list_indexes():
    return [d for d in os.listdir(INDEX_DIR) if os.path.isdir(os.path.join(INDEX_DIR, d))]

existing_indexes = list_indexes()

with st.form("index_form", clear_on_submit=False):
    # No columns, just one clear UI
    new_or_existing = st.radio(
        "What would you like to do?",
        ["Create new index", "Append to existing index"],
        horizontal=True,
        key="index_mode"
    )

    index_name = ""
    embedding_model = ""
    meta = {}

    if new_or_existing == "Append to existing index":
        if existing_indexes:
            index_name = st.selectbox("Select index to append", existing_indexes)
            index_path = os.path.join(INDEX_DIR, index_name)
            meta = read_index_metadata(index_path)
            emb_model_used = meta.get("embedding_model", default_embedding)
            st.info(
                f"Embedding model for this index: **{emb_model_used}** (cannot be changed)"
            )
            embedding_model = emb_model_used
        else:
            st.warning("No existing indexes to append to.")
            index_name = ""
            embedding_model = ""
            index_path = ""
    else:
        index_name = st.text_input("New index name")
        index_path = os.path.join(INDEX_DIR, index_name) if index_name else None
        embedding_model = st.selectbox(
            "Select embedding model",
            embedding_models,
            index=embedding_models.index(default_embedding) if default_embedding in embedding_models else 0
        ) if embedding_models else ""

    uploaded_files = st.file_uploader(
        "Upload files to index",
        type=["pdf", "docx", "md", "txt"],
        accept_multiple_files=True
    )

    urls_text = st.text_area("Optional: Enter one URL per line to index web content")
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

    ready = bool(index_name and (uploaded_files or urls))
    submit_btn = st.form_submit_button("🚀 Build/Update Index", disabled=not ready)

if submit_btn and index_name:
    start_time = time.time()
    st.info(f"Index target: `{index_name}` using embedding: `{embedding_model}`")
    documents = []

    uploaded_docs = []
    if uploaded_files:
        for file in uploaded_files:
            file_path = os.path.join(DOC_ROOT, file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
            uploaded_docs.append(file_path)
        st.success(f"Uploaded {len(uploaded_docs)} files.")

    if uploaded_docs:
        reader = SimpleDirectoryReader(input_dir=DOC_ROOT, recursive=False)
        all_docs = reader.load_data()
        for i, doc in enumerate(all_docs):
            st.write(f"Processing: {doc.metadata.get('file_name', 'Unnamed')}")
            documents.append(doc)
        st.success("✅ All local documents processed.")

    if urls:
        st.write("🔍 Fetching web documents...")
        web_docs = []
        for url in urls:
            try:
                doc = SimpleWebPageReader(html_to_text=True).load_data([url])
                web_docs.extend(doc)
            except Exception as e:
                st.warning(f"Failed to load {url}: {e}")
        documents.extend(web_docs)
        st.success("✅ All web documents processed.")

    Settings.embed_model = OllamaEmbedding(model_name=embedding_model, base_url=OLLAMA_BASE_URL)

    if new_or_existing == "Append to existing index" and os.path.exists(index_path):
        st.info(f"Appending to existing index `{index_name}`...")
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        try:
            index = load_index_from_storage(storage_context)
            index.insert_documents(documents)
            st.success(f"Documents added to index `{index_name}`.")
            write_index_metadata(index_path, embedding_model)
        except Exception as e:
            st.error(f"Failed to append to index: {e}")
    else:
        if os.path.exists(index_path):
            st.warning("Index name already exists! Pick a different name or choose 'Append'.")
        else:
            st.info(f"Building new index `{index_name}`...")
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=index_path)
            write_index_metadata(index_path, embedding_model)
            st.success(f"Index `{index_name}` created successfully in {time.time() - start_time:.1f} seconds.")

st.page_link("app.py", label="⬅️ Back to Chat", icon="💬")
