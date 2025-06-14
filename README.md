# 🚀 Jetson Copilot V3.1.2

A fully local, GPU-accelerated, hybrid-RAG AI assistant for NVIDIA Jetson AGX Orin (and beyond).

---

## 🔥 Features

- Fully self-hosted AI chat engine powered by Ollama
- Supports local model inference with streaming chat
- Hybrid RAG mode combining indexed documents + live uploaded files
- Model catalog intelligence powered by GPT for easy model evaluation
- Supports PDFs, DOCX, Markdown, TXT ingestion
- ARM64-native optimized build for Jetson Orin

---

## ⚙ Architecture

| Layer | Location |
|-------|----------|
| Ollama Server | Installed directly on Jetson host (ARM64 binary) |
| Ollama Model Files | `~/.ollama` on host |
| Streamlit App (Copilot) | Inside Docker container |
| Ollama Python Client (v0.5.1) | Inside Docker |
| LlamaIndex (v0.10.20 stack) | Inside Docker |
| Document Storage | Mounted index directory inside Docker |

---

## 🚀 Build Instructions (Jetson Copilot V3.1.2 Optimized Build)

### 1️⃣ Host dependencies (Jetson or DGX)

- Host Ollama server installed at version >= 0.1.27+
- Ollama ARM64 binary installed directly on host

Verify Ollama version:

```bash
ollama --version
# Should report: v0.1.27 (or newer)
You can safely upgrade Ollama on host by downloading the ARM64 binary from:
https://github.com/ollama/ollama/releases
```

2️⃣ Clone repository & build docker image
bash
Copy
Edit
git clone https://github.com/YOUR_REPO/jetson-copilot-clean
cd jetson-copilot-clean

# Build optimized Docker image
./build_copilot.sh  
✅ The first build may take several minutes  
✅ Subsequent rebuilds will be dramatically faster  

3️⃣ Run Jetson Copilot container  
```bash  
./run_copilot.sh
By default, Streamlit app will be served on:
http://localhost:8501/
```
The app inside Docker connects to Ollama running on the Jetson host using http://127.0.0.1:11434

🧬 Build System Optimization
⚡ Fully cached pip install layers (requirements.txt)  
⚡ App code changes no longer invalidate package layers  
⚡ Future rebuilds typically complete in ~30-60 seconds  
📝 Model Download  
Use the built-in model downloader inside the Streamlit app:  
Supports automatic pulling of models from Ollama library  
GPT-powered enrichment metadata automatically updates model catalog  
Jetson-safety indicators assist with proper model selection

🔧 File Structure
```bash
jetson-copilot-clean/
│
├── Dockerfile             # Fully optimized V3.1.2 build file
├── requirements.txt       # Python dependencies
├── build_copilot.sh       # Build script
├── run_copilot.sh         # Launch script
├── streamlit_app/
│   ├── app.py             # Main Streamlit app
│   ├── utils/
│   │   ├── func.py        # Utility functions
│   │   ├── constants.py   # App constants
│   │   └── model_catalog_utils.py  # GPT-powered model enrichment logic
│   └── pages/
│       └── download_model.py   # Ollama model download interface
└── Indexes/               # Document vector storage
```

💡 Roadmap  
✅ V3.1.2: Optimized build system  
🔄 V3.2.x: Optional multi-agent extensions  
🔄 V3.3.x: Cluster orchestration & distributed Ollama support

💖 Credits
NVIDIA Jetson AGX Orin  
Ollama model server  
LlamaIndex  
Streamlit