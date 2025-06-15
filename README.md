
# 🚀 Jetson Copilot V4.1

**Fully Modernized, Jetson-Optimized Ollama + Streamlit AI Assistant**

---

## ✅ Quick Start

### 1️⃣ Clone and enter project

```bash
git clone <your-repo-url> jetson-copilot-v4.1
cd jetson-copilot-v4.1
```

### 2️⃣ Install NVIDIA Container Runtime (Jetson Required)

Make sure you have JetPack SDK installed on your Jetson device.

```bash
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

### 3️⃣ Build Docker Image

```bash
./build_copilot.sh
```

### 4️⃣ Run the Copilot

```bash
./run_copilot.sh
```

---

## ✅ Features

- ✅ ARM64v8 fully compatible (Jetson Nano, Xavier, Orin etc)
- ✅ Streamlit 1.35+ UI
- ✅ Ollama API integration (v0.5.1+)
- ✅ LlamaIndex 0.12+ modernized RAG pipeline
- ✅ Streaming response buffering for smoother UI
- ✅ Dynamic document uploading (PDF, DOCX, Markdown, TXT)
- ✅ Full RAG Indexing (VectorStoreIndex with SentenceSplitter)

---

## ✅ Requirements

- Jetson device with JetPack SDK installed
- Docker with NVIDIA runtime enabled
- External Ollama model storage (`~/.ollama`) mounted on host for model access

---

## ✅ Models Used

- `llama3:latest`  → Chat LLM (ensure downloaded in Ollama)
- `mxbai-embed-large:latest`  → Embedding model

---

## ✅ Notes

- All uploaded files are temporarily indexed inside container memory unless persistent indexes are implemented.
- If you wish to mount your existing `~/.ollama` model cache into Docker, add this volume:

```bash
-v $HOME/.ollama:/root/.ollama
```

---

Built for production Jetson deployment.
