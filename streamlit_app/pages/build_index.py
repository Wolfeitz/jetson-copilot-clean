import streamlit as st
import os
import sys
import time
import pandas as pd
import logging
import ollama

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    SimpleDirectoryReader,
    Document,
    load_index_from_storage
)
from llama_index.core.settings import Settings
from llama_index.llms.ollama import Ollama
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

# Ensure embedding model is pulled
models = [model["model"] for model in ollama.list()["models"]]
if 'mxbai-embed-large:latest' not in models:
    with st.spinner("Downloading embedding model..."):
        ollama.pull("mxbai-embed-large")

Settings.embed_model = OllamaEmbedding(model_name="mxbai-embed-large:latest", base_url=OLLAMA_BASE_URL)

# Sidebar
with st.sidebar:
    st.header("📦 New Index Setup")
    index_name = st.text_input("Index Name:")
    index_path = os.path.join(INDEX_DIR, index_name) if index_name else None
    if index_name and os.path.exists(index_path):
        st.warning("Index name already exists!")
    
    st.info(
    "⚠️ **Note:** Jetson Copilot's current indexing architecture is tuned for collections of mostly unique, standalone documents. "
    "It is *not* optimized for aggregation or summarization across large log/event files or other high-volume, repetitive data sources."
    )

# ---- File Deletion UI ----
st.subheader("📄 Uploaded Documents in Workspace")

existing_files = [f for f in os.listdir(DOC_ROOT) if os.path.isfile(os.path.join(DOC_ROOT, f))]
deleted_any = False
for fname in existing_files:
    file_path = os.path.join(DOC_ROOT, fname)
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(fname)
    with col2:
        if st.button("❌ Delete", key=f"del_{fname}"):
            try:
                os.remove(file_path)
                st.success(f"Deleted {fname}")
                deleted_any = True
            except Exception as e:
                st.error(f"Error deleting {fname}: {e}")
if deleted_any:
    st.experimental_rerun()  # Refresh the UI after delete

# ---- Upload documents ----
st.subheader("⬆️ Upload New Files")
uploaded_files = st.file_uploader(
    "Upload files for indexing:",
    type=["pdf", "docx", "md", "txt"],
    accept_multiple_files=True
)

uploaded_docs = []
if uploaded_files:
    for file in uploaded_files:
        file_path = os.path.join(DOC_ROOT, file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
        uploaded_docs.append(file_path)
    st.success(f"Uploaded {len(uploaded_docs)} files.")

# ---- Optional URLs ----
st.subheader("🌐 Optional URLs (web scraping)")
urls_text = st.text_area("Enter one URL per line to pull web pages:")
urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

# ---- Build index ----
if st.button("🚀 Build Index", disabled=not index_name or (not existing_files and not urls)):
    start_time = time.time()
    documents = []

    if existing_files:
        reader = SimpleDirectoryReader(input_dir=DOC_ROOT, recursive=False)
        try:
            all_docs = reader.load_data()
            st.write(f"Loaded {len(all_docs)} documents:")
            for i, doc in enumerate(all_docs):
                st.write(f"Doc {i+1}: file_name={doc.metadata.get('file_name')}, file_path={doc.metadata.get('file_path')}, type={doc.metadata.get('file_type')}")
        except ImportError as e:
            st.error(f"Missing dependency: {e}")
            st.stop()
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i, doc in enumerate(all_docs):
            status_text.text(f"Processing document {i+1} of {len(all_docs)}: {doc.metadata.get('file_name', 'Unnamed')}")
            documents.append(doc)
            progress_bar.progress((i + 1) / len(all_docs))
        status_text.text("✅ All local documents processed.")

    if urls:
        st.write("🔍 Fetching web documents...")
        web_docs = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i, url in enumerate(urls):
            status_text.text(f"Scraping ({i+1}/{len(urls)}): {url}")
            try:
                doc = SimpleWebPageReader(html_to_text=True).load_data([url])
                web_docs.extend(doc)
            except Exception as e:
                st.warning(f"Failed to load {url}: {e}")
            progress_bar.progress((i + 1) / len(urls))
        documents.extend(web_docs)
        status_text.text("✅ All web documents processed.")

    if documents:
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=index_path)
        elapsed = time.time() - start_time
        st.success(f"Index '{index_name}' created successfully in {elapsed:.1f} seconds.")
    else:
        st.warning("No documents to index. Upload files or enter URLs above.")

# ---- Back link ----
st.page_link("app.py", label="⬅️ Back to Chat")
