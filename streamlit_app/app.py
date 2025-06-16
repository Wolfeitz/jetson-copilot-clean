import streamlit as st
import ollama
import io
import os
import tempfile
import logging
import sys
from PIL import Image
from llama_index.core.settings import Settings
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.file import PDFReader, DocxReader, MarkdownReader
from llama_index.readers.web import SimpleWebPageReader  # <- this is the missing import

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

st.set_page_config(page_title="Jetson Copilot V4.4.4 SaaS", page_icon="🤖")

AVATAR_AI = Image.open('./images/jetson-soc.png')
AVATAR_USER = Image.open('./images/user-purple.png')

DEFAULT_PROMPT = """You are a highly capable AI assistant. Use any document context provided to inform your answers.

Document Context:
{context_str}

Instructions:
Use both the chat history and document context to assist the user."""

INDEX_DIR = "Indexes"

# Model Loader
def load_models():
    try:
        response = ollama.list()
        models_raw = response.get("models", [])
        models = [model_entry["name"] for model_entry in models_raw if "name" in model_entry]
    except Exception as e:
        st.error(f"Failed to query Ollama models: {e}")
        models = []

    if 'llama3:latest' not in models:
        with st.spinner("Downloading llama3..."):
            ollama.pull("llama3")
            models.append("llama3:latest")

    if 'mxbai-embed-large:latest' not in models:
        with st.spinner("Downloading embedding model..."):
            ollama.pull("mxbai-embed-large")
            models.append("mxbai-embed-large:latest")

    return sorted(models)

if "models" not in st.session_state:
    st.session_state.models = load_models()

models = st.session_state.models

# Session State Init
if "memory" not in st.session_state:
    st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload documents or start chatting.", "avatar": AVATAR_AI}]
if "context_prompt" not in st.session_state:
    st.session_state.context_prompt = DEFAULT_PROMPT
if "rag_mode" not in st.session_state:
    st.session_state.rag_mode = False
if "active_index" not in st.session_state:
    st.session_state.active_index = None

# File Processor (used by BuildIndex only now)
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
        else:
            text = content.decode("utf-8", errors="ignore")
            docs = [Document(text=text)]
        documents.extend(docs)
    return documents

# Persistent Index Mgmt
def list_indexes():
    os.makedirs(INDEX_DIR, exist_ok=True)
    return [d for d in os.listdir(INDEX_DIR) if os.path.isdir(os.path.join(INDEX_DIR, d))]

def load_existing_index(index_name):
    storage_context = StorageContext.from_defaults(persist_dir=os.path.join(INDEX_DIR, index_name))
    return load_index_from_storage(storage_context)

# Sidebar UI
with st.sidebar:
    st.title("Jetson Copilot V4.4.4 SaaS")
    default_model = "llama3:latest" if "llama3:latest" in models else models[0]
    selected_model = st.selectbox("LLM Model", models, index=models.index(default_model))
    st.session_state["model"] = selected_model
    st.page_link("pages/download_model.py", label=" Download a new LLM", icon="➕")

    llm = Ollama(model=selected_model, request_timeout=300.0)
    embed_model = OllamaEmbedding("mxbai-embed-large:latest")
    Settings.llm = llm
    Settings.embed_model = embed_model

    st.toggle("Enable RAG", value=st.session_state.rag_mode, key="rag_mode", on_change=lambda: None)

    updated_prompt = st.text_area("System Prompt:", value=st.session_state.context_prompt, height=200)
    if updated_prompt != st.session_state.context_prompt:
        st.session_state.context_prompt = updated_prompt
        st.success("Prompt updated.")

    if st.session_state.rag_mode:
        st.subheader("RAG Index Management:")
        indexes = list_indexes()
        if indexes:
            selected_index = st.selectbox("Select RAG Index:", indexes, index=0)
            st.session_state.active_index = selected_index
        else:
            st.info("No indexes found.")
            st.session_state.active_index = None

        st.page_link("pages/build_index.py", label="🛠️ Build New Index")

# Chat flow
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["avatar"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": AVATAR_USER})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_AI):
        with st.spinner("Thinking..."):
            response, buffer, flush_every = "", "", 20
            placeholder = st.empty()

            if st.session_state.rag_mode and st.session_state.active_index:
                rag_index = load_existing_index(st.session_state.active_index)
                chat_engine = rag_index.as_chat_engine(
                    chat_mode="context",
                    memory=st.session_state.memory,
                    system_prompt=st.session_state.context_prompt,
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

# Chat reset
with st.sidebar:
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload documents or start chatting.", "avatar": AVATAR_AI}]
        st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
        st.success("Chat reset.")
