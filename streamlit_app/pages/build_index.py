import streamlit as st
import os
import sys
import time
import pandas as pd
import logging
import ollama

from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.core import StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.readers import SimpleWebPageReader

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# App title
st.set_page_config(page_title="Jetson Copilot - Build Index", page_icon="🛠️")

INDEX_DIR = "Indexes"
DOC_ROOT = "Documents"

# Ensure base directories exist
os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(DOC_ROOT, exist_ok=True)

# Model loader (ensure embedding model is pulled)
models = [model["name"] for model in ollama.list()["models"]]
if 'mxbai-embed-large:latest' not in models:
    with st.spinner("Downloading embedding model..."):
        ollama.pull("mxbai-embed-large")

# Embedding model is fixed for now to OllamaEmbedding
Settings.embed_model = OllamaEmbedding(model_name="mxbai-embed-large:latest")

# Sidebar: index name
with st.sidebar:
    st.header("📦 New Index Setup")

    index_name = st.text_input("Index Name:")
    index_path = os.path.join(INDEX_DIR, index_name) if index_name else None

    if index_name and os.path.exists(index_path):
        st.warning("Index name already exists!")

# Step 1: Upload documents
st.subheader("📄 Upload Files")

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

if uploaded_docs:
    st.success(f"Uploaded {len(uploaded_docs)} files.")

# Step 2: Optional URLs
st.subheader("🌐 Optional URLs (web scraping)")
urls_text = st.text_area("Enter one URL per line to pull web pages:")
urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

# Step 3: Build index button
if st.button("🚀 Build Index", disabled=not index_name or (not uploaded_files and not urls)):
    start_time = time.time()

    documents = []

    if uploaded_docs:
        reader = SimpleDirectoryReader(input_dir=DOC_ROOT, recursive=False)
        docs = reader.load_data()
        documents.extend(docs)
        st.write(f"Loaded {len(docs)} local documents.")

    if urls:
        web_docs = SimpleWebPageReader(html_to_text=True).load_data(urls)
        documents.extend(web_docs)
        st.write(f"Loaded {len(web_docs)} web documents.")

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=index_path)

    elapsed = time.time() - start_time
    st.success(f"Index '{index_name}' created successfully in {elapsed:.1f} seconds.")

# Link back to main chat page
st.page_link("app.py", label="⬅️ Back to Chat")
