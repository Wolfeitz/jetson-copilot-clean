import ollama
import streamlit as st
import time
import logging
import sys
import os

from llama_index.core import VectorStoreIndex, Settings, Document, StorageContext, load_index_from_storage
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.file import PyMuPDFReader, MarkdownReader, DocxReader

from PIL import Image
import tempfile
import io

# Add parent path to import our local utils
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import utils.func
import utils.constants as const
from utils import model_catalog_utils

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Streamlit page config
st.set_page_config(page_title="Jetson Copilot", menu_items=None)

# Load avatars
AVATAR_AI = Image.open('./images/jetson-soc.png')
AVATAR_USER = Image.open('./images/user-purple.png')

# Default system prompt (fully generalized now)
DEFAULT_PROMPT = """
You are a helpful assistant capable of answering any general question, and answering questions based on both indexed documents and uploaded files when available.

Use chat history, document context, and reasoning to help the user.
"""

# Session state initialization
if "memory" not in st.session_state:
    st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me anything!", "avatar": AVATAR_AI}
    ]

if "context_prompt" not in st.session_state:
    st.session_state.context_prompt = DEFAULT_PROMPT

if "use_index" not in st.session_state:
    st.session_state.use_index = False

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

# Utility functions
def find_saved_indexes():
    return utils.func.list_directories(const.INDEX_ROOT_PATH)

def load_index(index_name):
    Settings.embed_model = OllamaEmbedding("mxbai-embed-large:latest")
    dir = f"{const.INDEX_ROOT_PATH}/{index_name}"
    storage_context = StorageContext.from_defaults(persist_dir=dir)
    return load_index_from_storage(storage_context)

def process_uploaded_files(files):
    documents = []
    for file in files:
        file_content = file.read()
        file_name = file.name.lower()

        if file_name.endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            reader = PyMuPDFReader()
            docs = reader.load_data(tmp_path)

        elif file_name.endswith(".docx"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            reader = DocxReader()
            docs = reader.load_data(tmp_path)

        elif file_name.endswith(".md"):
            reader = MarkdownReader()
            docs = reader.load_data(file=io.BytesIO(file_content))

        elif file_name.endswith(".txt"):
            text = file_content.decode("utf-8", errors="ignore")
            docs = [Document(text=text, metadata={"filename": file_name})]

        else:
            text = file_content.decode("utf-8", errors="ignore")
            docs = [Document(text=text, metadata={"filename": file_name})]

        documents.extend(docs)

    return documents

# Ollama model listing
models = [model["name"] for model in ollama.list()["models"]]

# FULL bulletproof cold start check
if not models:
    st.warning("🚩 No models installed yet. Please download a model first.")
    st.stop()

# Safe model selector
if "llama3.1:8b" in models:
    default_model = "llama3.1:8b"
else:
    default_model = models[0]

st.session_state["model"] = st.selectbox("Choose LLM Model", models, index=models.index(default_model))

Settings.llm = Ollama(model=st.session_state["model"], request_timeout=300.0)

# Sidebar
with st.sidebar:
    st.title(":rocket: Jetson Copilot V3.1.1")
    st.subheader('Fully autonomous local AI assistant', divider='rainbow')

    st.page_link("pages/download_model.py", label="Download Models", icon="➕")

    prev_use_index = st.session_state.use_index
    st.session_state.use_index = st.toggle("Use RAG (document retrieval)", value=st.session_state.use_index)

    new_prompt = st.text_area("System prompt", st.session_state.context_prompt, height=200)
    if new_prompt != st.session_state.context_prompt:
        st.session_state.context_prompt = new_prompt
        st.success("System prompt updated!")

    uploaded_files = st.file_uploader("Upload files to chat context", type=["pdf", "txt", "docx", "md"], accept_multiple_files=True)
    if uploaded_files:
        new_docs = process_uploaded_files(uploaded_files)
        st.session_state.uploaded_docs.extend(new_docs)
        st.success("Files successfully uploaded!")

    if st.session_state.use_index:
        saved_index_list = find_saved_indexes()
        index_name = st.selectbox("Index", saved_index_list)

        if index_name:
            with st.spinner('Loading index...'):
                st.session_state.index = load_index(index_name)

            st.page_link("pages/build_index.py", label="Build Index", icon="🛠️")

    model_catalog_utils.sync_catalog()

    if st.button("🔁 Reset Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me anything!", "avatar": AVATAR_AI}
        ]
        st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
        st.session_state.uploaded_docs = []
        st.success("Chat reset.")

# Chat history display
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])

# Main chat loop
if prompt := st.chat_input("Enter prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": AVATAR_USER})

    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_AI):
        with st.spinner("Thinking..."):
            time.sleep(0.5)

            message = ""

            if st.session_state.use_index:
                permanent_docs = st.session_state.index.storage_context.docstore.docs.values()
                all_docs = list(permanent_docs) + st.session_state.uploaded_docs
                combined_index = VectorStoreIndex.from_documents(all_docs)

                chat_engine = combined_index.as_chat_engine(
                    chat_mode="context",
                    streaming=True,
                    memory=st.session_state.memory,
                    llm=Settings.llm,
                    context_prompt=st.session_state.context_prompt,
                    verbose=True
                )

                placeholder = st.empty()
                for chunk in chat_engine.stream_chat(prompt).response_gen:
                    message += chunk
                    placeholder.markdown(message)
            else:
                system_prompt = st.session_state.context_prompt
                messages_only = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                stream = ollama.chat(model=st.session_state["model"], messages=messages_only, stream=True)
                placeholder = st.empty()
                for chunk in stream:
                    message += chunk["message"]["content"]
                    placeholder.markdown(message)

            st.session_state.messages.append({"role": "assistant", "content": message, "avatar": AVATAR_AI})
