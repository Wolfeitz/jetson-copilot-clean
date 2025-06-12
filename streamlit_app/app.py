import ollama
import openai
import streamlit as st
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader, Document
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import PDFReader, DocxReader, MarkdownReader
from PIL import Image
import time
import logging
import sys
import io
import tempfile
import utils.func 
import utils.constants as const

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

st.set_page_config(page_title="Jetson Copilot", menu_items=None)

AVATAR_AI   = Image.open('./images/jetson-soc.png')
AVATAR_USER = Image.open('./images/user-purple.png')

DEFAULT_PROMPT = """You are a chatbot, able to have normal interactions, as well as talk about NVIDIA Jetson embedded AI computer.
Here are the relevant documents for the context:\n
{context_str}
\nInstruction: Use the previous chat history, or the context above, to interact and help the user."""

# --- Session State Initialization ---
if "memory" not in st.session_state:
    st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me any question about NVIDIA Jetson embedded AI computer!", "avatar": AVATAR_AI}
    ]

if "context_prompt" not in st.session_state:
    st.session_state.context_prompt = DEFAULT_PROMPT

if "use_index" not in st.session_state:
    st.session_state.use_index = False

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []  # store parsed documents

# --- Utility Functions ---
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
            reader = PDFReader()
            docs = reader.load_data(file=tmp_path)

        elif file_name.endswith(".docx"):
            reader = DocxReader()
            docs = reader.load_data(file=io.BytesIO(file_content))

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

# --- Model Setup ---
models = [model["name"] for model in ollama.list()["models"]]

if 'llama3:latest' not in models:
    with st.spinner('Downloading llama3 model ...'):
        ollama.pull('llama3')

if 'mxbai-embed-large:latest' not in models:
    with st.spinner('Downloading mxbai-embed-large model ...'):
        ollama.pull('mxbai-embed-large')

# --- Sidebar ---
with st.sidebar:
    st.title(":airplane: Jetson Copilot")
    st.subheader('Your local AI assistant on Jetson', divider='rainbow')

    default_model = "llama3:latest" if "llama3:latest" in models else models[0]
    st.session_state["model"] = st.selectbox("Choose your LLM", models, index=models.index(default_model))

    Settings.llm = Ollama(model=st.session_state["model"], request_timeout=300.0)
    st.page_link("pages/download_model.py", label=" Download a new LLM", icon="➕")

    prev_use_index = st.session_state.use_index
    st.session_state.use_index = st.toggle("Use RAG (adds context from documents)", value=st.session_state.use_index)

    new_prompt = st.text_area("System prompt", st.session_state.context_prompt, height=240)
    prompt_changed = new_prompt != st.session_state.context_prompt
    if prompt_changed:
        st.session_state.context_prompt = new_prompt
        st.success("System prompt updated!")

    uploaded_files = st.file_uploader("Drop files to add to context", type=["pdf", "txt", "docx", "md"], accept_multiple_files=True)
    
    if uploaded_files:
        new_docs = process_uploaded_files(uploaded_files)
        st.session_state.uploaded_docs.extend(new_docs)
        st.success("Uploaded documents loaded into session!")

    if st.session_state.use_index:
        saved_index_list = find_saved_indexes()
        index_name = st.selectbox("Index", saved_index_list)

        if index_name:
            with st.spinner('Loading Index...'):
                st.session_state.index = load_index(index_name)

            st.page_link("pages/build_index.py", label=" Build a new index", icon="➕")

# --- Chat function with dynamic hybrid rebuild ---
def get_current_chat_engine():
    if not st.session_state.use_index:
        return None

    # Load permanent docs from storage (compatible with your version)
    permanent_docs = st.session_state.index.storage_context.docstore.docs.values()
    all_docs = list(permanent_docs) + st.session_state.uploaded_docs

    # Build hybrid index dynamically
    combined_index = VectorStoreIndex.from_documents(all_docs)

    chat_engine = combined_index.as_chat_engine(
        chat_mode="context",
        streaming=True,
        memory=st.session_state.memory,
        llm=Settings.llm,
        context_prompt=st.session_state.context_prompt,
        verbose=True
    )
    return chat_engine

# --- Display chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])

# --- Handle user input ---
if prompt := st.chat_input("Enter prompt here.."): 
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": AVATAR_USER})

    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_AI):
        with st.spinner("Thinking..."):
            time.sleep(1)

            chat_engine = get_current_chat_engine()
            if chat_engine:
                response_stream = chat_engine.stream_chat(prompt)
                message = st.write_stream(response_stream.response_gen)
            else:
                system_prompt = st.session_state.context_prompt
                messages_only = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]
                stream = ollama.chat(model=st.session_state["model"], messages=messages_only, stream=True)
                message = ""
                for chunk in stream:
                    message += chunk["message"]["content"]
                    st.write(chunk["message"]["content"])

            st.session_state.messages.append({"role": "assistant", "content": message, "avatar": AVATAR_AI})

# --- Reset Chat & Export ---
with st.sidebar:
    if st.button("\U0001F504 Reset Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me any question about NVIDIA Jetson embedded AI computer!", "avatar": AVATAR_AI}
        ]
        st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
        st.session_state.uploaded_docs = []
        st.success("Chat history reset.")

    if st.button("\U0001F4C4 Export Transcript"):
        transcript = "\n\n".join(
            f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages if m['role'] in ['user', 'assistant']
        )
        buffer = io.BytesIO()
        buffer.write(transcript.encode())
        buffer.seek(0)
        st.download_button("Download Chat (.txt)", data=buffer, file_name="chat_transcript.txt", mime="text/plain")
