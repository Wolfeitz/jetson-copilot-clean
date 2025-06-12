
# Jetson Copilot Clean Build V1.0 🚀

> **Private AI Assistant for NVIDIA Jetson — Fully Modernized, Ollama-powered, and RAG-ready**

---

## ✨ Overview

Jetson Copilot is a **local AI assistant** designed for NVIDIA Jetson devices. This modernized build fully replaces the original NVIDIA Copilot reference container with:

- ✅ Fully public Docker build (no NVIDIA private `nvcr.io` access required)
- ✅ Python 3.10 (fully compatible with latest LlamaIndex releases)
- ✅ Modular LlamaIndex hybrid RAG (Retrieval-Augmented Generation)
- ✅ Ollama 0.9.0 server running directly on Jetson host (ARM64 native)
- ✅ Simplified, reproducible, open-source friendly build process
- ✅ Compatible with JetPack 6.0 GA (L4T 36.4.0)

---

## 🔥 Key Differences from NVIDIA Reference Build

| Component | This Build | NVIDIA Original |
|------------|-------------|-------------------|
| Ollama version | 0.9.0 native host | Frozen older client |
| Ollama location | Runs directly on Jetson host | Bundled inside Docker |
| LlamaIndex version | 0.10.20 modular | 0.11.17 frozen |
| Python version | 3.10 | 3.8 |
| Docker base | Ubuntu 22.04 ARM64 (public) | NVIDIA private L4T |
| NVIDIA login required | ❌ No | ✅ Yes |
| Fully reproducible public build | ✅ Yes | ❌ No |
| Fully open-source safe | ✅ Yes | ❌ No |

---

## ⚙️ System Requirements

- Jetson device with JetPack 6.0 GA or newer (L4T 36.4.0+)
- NVIDIA container runtime (`nvidia-docker2`)
- Ollama 0.9.0 installed directly on Jetson host (ARM64-native)
- Docker installed

---

## 🚀 Install Instructions

### 1️⃣ Install Ollama (directly on Jetson host)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama version  # Verify version is 0.9.0 or newer
```

### 2️⃣ Pull LLM models on host

```bash
ollama pull llama3
ollama pull llama4
ollama pull phi3
ollama pull mistral
ollama pull codellama
```

### 3️⃣ Clone and build Jetson Copilot

```bash
git clone https://github.com/YOUR_REPO/jetson-copilot-clean.git
cd jetson-copilot-clean

chmod +x build_copilot.sh run_copilot.sh

./build_copilot.sh
./run_copilot.sh
```

---

## 🌐 Accessing Jetson Copilot

After launch, visit:

- `http://localhost:8501/` (on Jetson directly)
- `http://<JETSON_LAN_IP>:8501/` (from other machines on same network)

The `run_copilot.sh` script will automatically display your IP addresses.

---

## 🧠 How To Use Jetson Copilot

### Plain Chat (no RAG)

You can immediately chat with LLM models you’ve downloaded via Ollama.

### RAG Mode (Use Documents & Knowledge)

Toggle **RAG mode** inside Streamlit sidebar to enable Retrieval-Augmented Generation using:

- Pre-built indexes (if available)
- Dynamically uploaded documents

You can build your own indexes directly within the app interface.

---

## 🗂 Directory Layout

```bash
jetson-copilot-clean/
├── Dockerfile
├── build_copilot.sh
├── run_copilot.sh
├── streamlit_app/
│   ├── app.py
│   ├── utils/
│   ├── images/
└── indexes/  # Optional pre-built indexes
```

---

## 🧪 Development Workflow

- Streamlit supports auto-reloading — simply edit `streamlit_app/app.py` while app is running.
- You can stop/restart container via `run_copilot.sh` easily.

---

## 🐳 Docker Build Notes

- Fully public Docker image using `arm64v8/ubuntu:22.04`
- Python 3.10 fully supported
- NVIDIA container runtime handles GPU passthrough (`--runtime=nvidia` used in launcher)

---

## 🩺 Troubleshooting

### Docker Permission Errors

Ensure your Jetson user is part of docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

If issues persist, logout and reboot.

### Model not found error

Be sure you’ve pulled models directly via `ollama pull` on Jetson host before running app.

---

## 📜 License

Same as original NVIDIA Copilot: Apache 2.0

---

## ❤️ Credits

- Forked and fully modernized from NVIDIA Jetson Copilot reference
- Heavy lifting by [human + AI](https://chat.openai.com)

---

🚀 **Fully private, on-device, cloud-free AI Copilot for Jetson. Production-ready.**
