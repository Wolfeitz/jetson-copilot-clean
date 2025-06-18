# 🚀 Jetson Copilot V4.x

**Fully Modernized, Jetson-Optimized Ollama + Streamlit AI Assistant**

---

## ✅ Quick Start

### 1️⃣ Clone and Enter Project

```bash
git clone <your-repo-url> jetson-copilot
cd jetson-copilot
```

2️⃣ Install NVIDIA Container Runtime (Jetson Required)
You need JetPack SDK and Docker with NVIDIA runtime.

```bash
sudo apt update
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

If you’re using an AGX Orin, Xavier, Nano, etc., JetPack SDK must already be set up.

3️⃣ Build Docker Image
```bash
./build_copilot.sh
```

4️⃣ Run Jetson Copilot
```bash
./run_copilot.sh
```

You will see URLs for localhost, local network, and (if routed) your public IP.

---

✅ Features
- ARM64v8 fully compatible (Jetson Orin, Xavier, Nano)
- Streamlit UI with modern chat, RAG, and streaming responses
- Ollama API integration (v0.5.1+)
- LlamaIndex (>=0.12) vector-based RAG
- Live model catalog: View, search, and update available LLM and embedding models
- Upload, index, and query PDFs, DOCX, Markdown, TXT (with optional web scraping)
- Persistent RAG indexes
- Customizable system prompt
- Full device-local or DGX-ready operation

---

✅ System Requirements
- NVIDIA Jetson device (Orin, Xavier, Nano, etc.) with JetPack
- Docker with NVIDIA runtime (nvidia-container-toolkit)
- At least 16GB RAM (for efficient RAG, more recommended)
- Ollama running on host (or separate container, see below)
- ARM64 support (this image is built for ARM, not x86_64)

---

✅ Model Management
How It Works
- Models are managed by Ollama on the host.
- The app connects via OLLAMA_BASE_URL (default: http://localhost:11434).
- Model metadata is stored in /usr/share/ollama/model_catalog.json (host) and mounted read-only into the app container.

Add New Models
```bash
ollama pull <model-name>
```

Models appear in the UI automatically. To update metadata (RAM, Jetson safety, "Why Choose", etc.), simply edit `model_catalog`.json on the host and refresh the UI.

Example Models
- llama3:latest — main chat LLM
- mxbai-embed-large:latest — embedding for RAG
- Others supported (see model list in-app)

Notes
- To mount your host’s models into a custom container:

```bash
-v $HOME/.ollama:/root/.ollama
```
---

✅ Indexes
- Indexes are stored in the Indexes/ directory, inside the container by default.
- Each index tracks its embedding model in Indexes/<index_name>/metadata.json.
- When extending an index, embedding model is locked for consistency.

Tip: If you want persistent or shared indexes, mount Indexes/ as a Docker volume.

---

✅ Environment Variables
- OLLAMA_BASE_URL — location of the Ollama API (default: http://localhost:11434)
- MODEL_CATALOG_PATH — path to model catalog (/app/model_catalog.json by default)

---

✅ Usage
- Browse to:
    http://localhost:8501 (or as shown in your terminal)
- Upload documents, build indexes, run RAG-enabled chat, or just use as a standalone chat AI.
- All settings (LLM selection, RAG toggle, prompt, etc.) are persisted between screens.

---

✅ Troubleshooting
- No models found?
    Ensure Ollama is running on the host and at least one model is pulled.
- GPU not used?
    Make sure you ran Docker with --runtime=nvidia and your Jetson device has NVIDIA drivers/JetPack.
- Indexes or catalog not persisting?
    Mount Indexes/ and /usr/share/ollama/model_catalog.json from the host as Docker volumes.
- Errors with document types?
    Some formats (like DOCX) require additional Python packages (docx2txt, etc.).  
    Add via pip install -r requirements.txt or update your container.

---

✅ Advanced: DGX/Cluster Use
- On DGX, use --gpus all instead of --runtime=nvidia in run_copilot.sh.
- You may run Ollama and Copilot as separate containers, and connect via API.
- For scaling, use a shared volume for model storage and (optionally) for indexes.

---

✅ Contributions & Support
- PRs welcome!
- If you find a bug, open an issue with system details.
- For NVIDIA Jetson/ARM-specific help, visit the NVIDIA developer forums.

---

Built for production Jetson deployment, but now supports DGX and multi-container clusters!