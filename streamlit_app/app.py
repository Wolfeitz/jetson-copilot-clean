import streamlit as st
import ollama
import io
import os
import tempfile
import logging
import sys
import json
from PIL import Image
from llama_index.core import (
    Settings, 
    Document,
    load_index_from_storage,
    SimpleDirectoryReader
)
from llama_index.core.storage import StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.memory import ChatMemoryBuffer

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ["OLLAMA_HOST"] = OLLAMA_BASE_URL
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

def is_embedding_model(model_name):
    return (
        "embed" in model_name.lower() or
        "embedding" in model_name.lower() or
        "mxbai" in model_name.lower() or
        "bge" in model_name.lower()
    )

# Helper to load embedding model from index metadata.json
def get_embedding_for_index(index_name):
    meta_path = os.path.join(INDEX_DIR, index_name, "metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)
                return meta.get("embedding_model")
        except Exception:
            return None
    return None

# Model Loader - loads from Ollama, returns only host models, sorted
def load_models():
    try:
        response = ollama.list()
        models_raw = response.get("models", [])
        models = [
            m.get("name") or m.get("model")
            for m in models_raw if (m.get("name") or m.get("model"))
        ]
    except Exception as e:
        st.error(f"Failed to query Ollama models: {e}")
        models = []
    return sorted(models)

# Session state: Model list always loaded
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

# --- Filter LLM models (for dropdown) ---
llm_models = [m for m in models if not is_embedding_model(m)]
default_model = "llama3:latest" if "llama3:latest" in llm_models else (llm_models[0] if llm_models else None)
selected_model = st.session_state.get("model", default_model)
if selected_model not in llm_models:
    selected_model = default_model

# --- Get all embedding models for later checking ---
embedding_models = [m for m in models if is_embedding_model(m)]
default_embedding = "mxbai-embed-large:latest" if "mxbai-embed-large:latest" in embedding_models else (embedding_models[0] if embedding_models else None)

# Sidebar UI
with st.sidebar:
    st.title("Jetson Copilot V4.4.4 SaaS")

    # LLM dropdown -- only non-embedding models
    if llm_models:
        selected_model = st.selectbox("LLM Model", llm_models, index=llm_models.index(selected_model) if selected_model in llm_models else 0)
        st.session_state["model"] = selected_model
    else:
        st.warning("No language models found on host.")
        st.session_state["model"] = None

    st.page_link("pages/model_list.py", label=" Available Models", icon="🧠")

    # RAG toggle and system prompt
    st.toggle("Enable RAG", value=st.session_state.rag_mode, key="rag_mode", on_change=lambda: None)
    updated_prompt = st.text_area("System Prompt:", value=st.session_state.context_prompt, height=200)
    if updated_prompt != st.session_state.context_prompt:
        st.session_state.context_prompt = updated_prompt
        st.success("Prompt updated.")

    # Index management and embedding model tracking
    if st.session_state.rag_mode:
        st.subheader("RAG Index Management:")
        # List indexes
        os.makedirs(INDEX_DIR, exist_ok=True)
        indexes = [d for d in os.listdir(INDEX_DIR) if os.path.isdir(os.path.join(INDEX_DIR, d))]
        if indexes:
            selected_index = st.selectbox("Select RAG Index:", indexes, index=0)
            st.session_state.active_index = selected_index
        else:
            st.info("No indexes found.")
            st.session_state.active_index = None

        st.page_link("pages/build_index.py", label="🛠️ Manage Indexes")

        # -- Embedding model info for selected index --
        index_embed = None
        if st.session_state.active_index:
            index_embed = get_embedding_for_index(st.session_state.active_index)
            if index_embed:
                st.markdown(
                    f"**Embedding model for this index:** <span style='color: green'>{index_embed}</span>",
                    unsafe_allow_html=True
                )
                if index_embed not in embedding_models:
                    st.error(
                        f"⚠️ The embedding model used for this index ('{index_embed}') is not currently available on the host. "
                        "Queries may fail or produce unexpected results."
                    )
            else:
                st.warning("Could not determine embedding model for this index. (Was it built with an older version?)")

        # Show which embedding model is actually in use (or will be)
        # We align the embedding model to match the index if possible
        used_embedding = index_embed if index_embed else default_embedding
        if used_embedding and used_embedding in embedding_models:
            Settings.embed_model = OllamaEmbedding(used_embedding, base_url=OLLAMA_BASE_URL)
        else:
            Settings.embed_model = OllamaEmbedding(default_embedding, base_url=OLLAMA_BASE_URL)

# Always set the LLM model
llm = Ollama(model=selected_model, request_timeout=300.0, base_url=OLLAMA_BASE_URL) if selected_model else None
Settings.llm = llm

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
                rag_index = load_index_from_storage(
                    StorageContext.from_defaults(persist_dir=os.path.join(INDEX_DIR, st.session_state.active_index))
                )
                chat_engine = rag_index.as_chat_engine(
                    chat_mode="context",
                    memory=st.session_state.memory,
                    system_prompt=st.session_state.context_prompt,
                    streaming=True,
                    similarity_top_k=12  # or whatever your default/top_k needs
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
                # --- ALWAYS include latest system prompt at top, then actual chat history (user/assistant only) ---
                system_prompt = st.session_state.context_prompt
                chat_history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                    if m["role"] in ("user", "assistant")
                ]
                messages_input = [{"role": "system", "content": system_prompt}] + chat_history

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
