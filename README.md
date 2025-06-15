# 🚀 Jetson Copilot V3.1.3

A fully self-hosted, GPU-accelerated, hybrid-RAG AI assistant for NVIDIA Jetson AGX Orin — built for personal use today, SaaS scale tomorrow.

---

## Jetson Copilot V3.2 🚀

An advanced, containerized local AI assistant designed for Jetson Orin AGX (and portable to DGX / SaaS stacks).  
This version introduces modernized builds, faster dependency resolution, fully isolated environments, and simplified maintenance for stable operation.


## 🔥 What's new in V3.1.3

- 🏋️ Fully minimized Docker image (sub-1GB builds)
- 🔌 Ollama fully externalized (host-managed models)
- 📦 Docker image holds only Streamlit app + core logic
- 🧠 SaaS-aligned architecture for future scale out
- 📄 Full support for PDF, Word, Markdown, TXT ingestion (OCR intentionally excluded)
- 📊 Tools for full Docker lifecycle management included

---

## Features

- ✅ Runs local Ollama models
- ✅ Document ingestion (PDF, DOCX, TXT, Web)
- ✅ Isolated per-container vector store
- ✅ Full GPU acceleration on Jetson Orin AGX
- ✅ Fully modernized package resolver (pip-tools based)
- ✅ 100% reproducible builds with pinned dependencies
- ✅ Fast rebuilds with optimized Docker layering

---

## 🏗 System Architecture

| Layer | Location |
|-------|----------|
| Ollama server | Host Jetson OS |
| Ollama models | `~/.ollama` (host filesystem) |
| Streamlit app | Inside Docker |
| Vector indexes | Docker-mounted volumes |
| Docker image | Slim, portable, version-locked |

---

## 🚀 Build & Run Instructions

### 1️⃣ Install Ollama server on host (Jetson AGX Orin)
```bash
ollama --version
```
- Recommended: Ollama 0.5.1 or higher
- Download directly for ARM64: https://github.com/ollama/ollama/releases

### 2️⃣ Clone this repository
```bash
git clone https://github.com/YOUR_REPO/jetson-copilot-clean
cd jetson-copilot-clean
```

### 3️⃣ Build Docker container
```bash
./build_copilot.sh
```
- Build completes in ~1-2 minutes after first run.
- Uses Docker host networking for Jetson compatibility.

### 4️⃣ Run Copilot container
```bash
./run_copilot.sh
```
- Launches Streamlit app on http://localhost:8501/

## 📦 Directory Structure
```bash
jetson-copilot-clean/
│
├── Dockerfile
├── requirements.txt
├── build_copilot.sh
├── run_copilot.sh
│
├── streamlit_app/
│   ├── app.py
│   ├── utils/
│   └── pages/
│
├── Indexes/    (mounted vector storage)
│
└── tools/
    ├── docker_reset.sh
    ├── docker_clean.sh
    ├── docker_nuke.sh
    └── README.md (tools documentation)
```

## Dockerfile Build Process
- Uses Ubuntu 22.04 ARM64v8
- Python 3.10 environment
- Modern pip-tools build system to solve dependency conflicts
- Models are stored on host machine and mounted via Ollama

---

## Requirements File Management
- Edit requirements.in to add/remove packages
- Run pip-compile requirements.in (either on host or during Docker build)
- Do NOT hand-edit requirements.txt

---

## ⚠ Known Current Limitations
- Current build requires stable internet during pip install
- LlamaIndex core package dependency versions can still occasionally drift.
- OCR-based ingestion still disabled by default (pending Jetson optimization)

---

## Next Steps
- ✅ v3.2 build stabilization ✅
- ⏩ Future: SaaS-ready scalable multi-tenant architecture
- ⏩ Optional: Jetson vs DGX optimized runtime flags

---

## 🛠 Docker Utility Tools (Inside /tools)
- Script	Purpose
- docker_reset.sh	Safely reset containers, volumes, images
- docker_clean.sh	Deeper cleanup of unused Docker resources
- docker_nuke.sh	Full Docker wipe (dangerous, but safe with confirmation)  
✅ See /tools/README.md for full instructions.


## 🔧 Jetson Optimized — SaaS Future Ready
- ✅ Designed for Jetson AGX Orin edge deployments
- ✅ Structured for DGX, Kubernetes, SaaS expansion
- ✅ Stateless app container
- ✅ External models & indexes
- ✅ RAG future-ready architecture

## 📈 SaaS Roadmap
| Phase |	Milestone |
|-----|----------|
| V3.1.x |	Jetson Copilot stabilized |
| V3.2.x |	SaaS-ready API layer extraction |
| V4.x |	DGX multi-tenant deployments |
| V5.x |	Full cloud-native managed clusters |

---

## 📝 Credits
- NVIDIA Jetson AGX Orin
- [Tutorial - Jetson Copilot](https://www.jetson-ai-lab.com/tutorial_jetson-copilot.html)
- Ollama LLM Inference Server
- LlamaIndex (RAG architecture)
- Streamlit App Layer
- Community Contributions