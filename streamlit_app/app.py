import streamlit as st
import ollama
import time
import os
import io
import tempfile
import logging
import sys
from PIL import Image
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.file import PDFReader, DocxReader, MarkdownReader

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# App configuration
st.set_page_config(page_title="Jetson Copilot V4", page_icon="🤖")

# Load avatars
AVATAR_AI = Image.open('./images/jetson-soc.png')
AVATAR_USER = Image.open('./images/user-purple.png')

# Default system prompt
DEFAULT_PROMPT = """You are a highly capable AI assistant.
Use any document context provided to inform your answers.

Document Context:
{context_str}

Instructions:
Use both the chat history and document context to assist the user."""

# Ensure models are available
def ensure_models():
    try:
        response = ollama.list()
        models_raw = list(response)  # normalize tuple/list
        models = []
        for model_entry in models_raw:
            if isinstance(model_entry, dict) and "name" in model_entry:
                models.append(model_entry["name"])
    except Exception as e:
        st.error(f"Failed to query Ollama models: {e}")
        models = []

    if 'llama3:latest' not in models:
        with st.spinner("Downloading llama3 model..."):
            ollama.pull("llama3")
            models.append("llama3:latest")

    if 'mxbai-embed-large:latest' not in models:
        with st.spinner("Downloading embedding model..."):
            ollama.pull("mxbai-embed-large")
            models.append("mxbai-embed-large:latest")

    return sorted(models)

# Initialize models
models = ensure_models()

# Initialize session state
if "memory" not in st.session_state:
    st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload documents or start chatting.", "avatar": AVATAR_AI}]
if "context_prompt" not in st.session_state:
    st.session_state.context_prompt = DEFAULT_PROMPT
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []
if "rag_mode" not in st.session_state:
    st.session_state.rag_mode = False

# File processor
class Document:
    def __init__(self, text):
        self.text = text

def process_uploaded_files(files):
    documents = []
    for file in files:
        content = file.read()
        name = file.name.lower()
        if name.endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                reader = PDFReader()
                docs = reader.load_data(tmp.name)
        elif name.endswith(".docx"):
            reader = DocxReader()
            docs = reader.load_data(io.BytesIO(content))
        elif name.endswith(".md"):
            reader = MarkdownReader()
            docs = reader.load_data(io.BytesIO(content))
        elif name.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")
            docs = [Document(text=text)]
        else:
            text = content.decode("utf-8", errors="ignore")
            docs = [Document(text=text)]
        documents.extend(docs)
    return documents

# Sidebar
with st.sidebar:
    st.title("Jetson Copilot V4")
    st.subheader("SaaS Modern Build")

    default_model = "llama3:latest" if "llama3:latest" in models else models[0]
    selected_model = st.selectbox("LLM Model", models, index=models.index(default_model))
    st.session_state["model"] = selected_model

    # Initialize Ollama LLM + embedding
    llm = Ollama(model=selected_model, request_timeout=300.0)
    embed_model = OllamaEmbedding("mxbai-embed-large:latest")

    st.session_state.rag_mode = st.toggle("Use RAG indexing", value=st.session_state.rag_mode)

    updated_prompt = st.text_area("System Prompt:", value=st.session_state.context_prompt, height=200)
    if updated_prompt != st.session_state.context_prompt:
        st.session_state.context_prompt = updated_prompt
        st.success("Updated system prompt.")

    uploaded = st.file_uploader("Upload documents", type=["pdf", "docx", "md", "txt"], accept_multiple_files=True)
    if uploaded:
        docs = process_uploaded_files(uploaded)
        st.session_state.uploaded_docs.extend(docs)
        st.success("Documents loaded.")

# Build RAG index
def build_rag_index():
    if not st.session_state.uploaded_docs:
        return None
    parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    index = VectorStoreIndex.from_documents(st.session_state.uploaded_docs, transformations=[parser])
    return index

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["avatar"]):
        st.markdown(msg["content"])

# Chat handling
if prompt := st.chat_input("Enter your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": AVATAR_USER})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_AI):
        with st.spinner("Generating response..."):
            response = ""
            buffer = ""
            flush_every = 20  # characters to buffer before updating UI
            placeholder = st.empty()

            if st.session_state.rag_mode and st.session_state.uploaded_docs:
                rag_index = build_rag_index()
                chat_engine = rag_index.as_chat_engine(
                    chat_mode="context",
                    memory=st.session_state.memory,
                    system_prompt=st.session_state.context_prompt,
                    llm=llm,
                    streaming=True
                )
                stream = chat_engine.stream_chat(prompt)
                for chunk in stream.response_gen:
                    buffer += chunk
                    if len(buffer) >= flush_every:
                        response += buffer
                        placeholder.markdown(response)
                        buffer = ""
                if buffer:
                    response += buffer
                    placeholder.markdown(response)
            else:
                system_prompt = st.session_state.context_prompt
                messages_input = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]
                stream = ollama.chat(model=selected_model, messages=messages_input, stream=True)
                for chunk in stream:
                    piece = chunk["message"]["content"]
                    buffer += piece
                    if len(buffer) >= flush_every:
                        response += buffer
                        placeholder.markdown(response)
                        buffer = ""
                if buffer:
                    response += buffer
                    placeholder.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response, "avatar": AVATAR_AI})

# Sidebar tool: Reset chat
with st.sidebar:
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload documents or start chatting.", "avatar": AVATAR_AI}]
        st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
        st.session_state.uploaded_docs = []
        st.success("Chat reset.")
