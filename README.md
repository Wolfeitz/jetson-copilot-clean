
Jetson Copilot Clean Build V2.0 🚀

Private AI Assistant for NVIDIA Jetson — Fully Modernized, Ollama-powered, and RAG-ready

---

✨ Overview

Jetson Copilot is a local AI assistant designed for NVIDIA Jetson devices. This fully modernized build replaces NVIDIA’s reference container with:

- Fully public Docker build (no NVIDIA private nvcr.io access required)
- Python 3.10 (fully compatible with latest LlamaIndex releases)
- Modular LlamaIndex hybrid RAG (Retrieval-Augmented Generation)
- Ollama 0.9.0 server running directly on Jetson host (ARM64 native)
- Simplified, reproducible, open-source friendly build process
- Compatible with JetPack 6.0 GA (L4T 36.4.0)

---

System Requirements

- Jetson device with JetPack 6.0 GA or newer
- NVIDIA container runtime (nvidia-docker2)
- Docker installed
- Ollama installed directly on Jetson host

---

🚀 Install Instructions

1️⃣ Install Ollama (directly on Jetson host)

curl -fsSL https://ollama.com/install.sh | sh
ollama version
# Confirm version is 0.9.0+

2️⃣ Pull LLM models on host

ollama pull llama3
ollama pull llama4
ollama pull phi3
ollama pull mistral
ollama pull codellama

3️⃣ Clone and build Jetson Copilot

git clone https://github.com/YOUR_REPO/jetson-copilot-clean.git
cd jetson-copilot-clean

chmod +x build_copilot.sh run_copilot.sh

./build_copilot.sh
./run_copilot.sh

---

🌐 Access Jetson Copilot

After launch, access the UI at:

- http://localhost:8501/ (local Jetson)
- http://<JETSON_LAN_IP>:8501/ (local network access)

The run_copilot.sh script will display your IP addresses.

---

🧠 Using Jetson Copilot

Pure Chat Mode (no RAG)

- Immediately chat with LLM models pulled via Ollama.

RAG Mode (Document-Aware)

- Enable RAG toggle in sidebar.
- Upload files or load pre-built indexes to augment responses.
- Supports: pdf, txt, docx, md files.

---

🗂 Folder Structure

jetson-copilot-clean/
├── Dockerfile
├── build_copilot.sh
├── run_copilot.sh
├── streamlit_app/
│   ├── app.py
│   ├── utils/
│   │   ├── constants.py
│   │   └── func.py
│   ├── images/
└── indexes/ (optional persistent indexes)

---

🩺 Troubleshooting

Docker Permission

sudo usermod -aG docker $USER
newgrp docker

Ollama Model Not Found

Ensure models are pulled directly via ollama pull on the host.

---

❤️ Credits

- Original concept from NVIDIA Jetson Copilot
- Fully modernized by Wolfeitz + AI (ChatGPT) collaboration

---

🚀 Fully private, on-device, cloud-free AI Copilot for Jetson — PRODUCTION READY.
