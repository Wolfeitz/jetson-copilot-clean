# Ollama Model & Model Catalog Architecture

## 🗂️ Where Are My Models?

**All models pulled with Ollama are stored on the host in:**

/usr/share/ollama/.ollama/models


- This is true for both Jetson and DGX setups.
- This is NOT the same as `/app/ollama_models` (no longer used).
- The models are owned by the `ollama` system user; this location is their home.

## 🤖 Jetson vs DGX: Architecture Overview

### Jetson (Orin, Nano, etc.)

- **Ollama server** runs directly on the Jetson host, typically as the `ollama` system user.
- **App containers** (Streamlit, RAG, etc.) connect to the Ollama server via `http://localhost:11434`.
- **Model catalog** is stored in `/usr/share/ollama/model_catalog.json` on the host and mounted read-only into the app container at `/app/model_catalog.json`.

### DGX or Workstation

- **Ollama server** runs directly on the DGX host, or in its own container with access to the system’s GPUs (`--gpus all`).
- **App containers** connect to Ollama server just like on Jetson.
- **Model catalog** is also stored and mounted as above.

**On both platforms:**  
- Model files are never inside the app container.  
- The model catalog file is shared via Docker volume mount for instant updates.

---

## 🔄 How To Update the Model Catalog

1. **Move or copy the catalog file to the Ollama directory:**
    ```bash
    sudo cp ./streamlit_app/model_catalog.json /usr/share/ollama/model_catalog.json
    ```
2. **Set permissions so the container/app can read it:**
    ```bash
    sudo chmod 644 /usr/share/ollama/model_catalog.json
    ```
3. **(If using Docker Compose or `docker run`)**  
   Make sure your `docker run` command or `docker-compose.yml` has:
    ```bash
    -v /usr/share/ollama/model_catalog.json:/app/model_catalog.json:ro
    ```
    so your app always reads the latest catalog from the host.

**No container rebuild is needed when updating this file!**

---

## 🛑 DO NOT:

- **Do not** put models or model catalogs inside the app container’s filesystem—they will be lost on rebuild.
- **Do not** try to “pull” models from inside the app container; always use Ollama on the host.

---

## 📌 Summary Table

| What?              | Location (Host)                       | Location (In Container)     | Notes                     |
|--------------------|---------------------------------------|-----------------------------|---------------------------|
| Models             | `/usr/share/ollama/.ollama/models`    | N/A                         | Managed by Ollama daemon  |
| Model Catalog JSON | `/usr/share/ollama/model_catalog.json`| `/app/model_catalog.json`   | Mount as read-only        |

---

## 🛠️ Need to Add a New Model?

1. On the host, pull it with:
    ```
    ollama pull <model-name>
    ```
2. Edit `/usr/share/ollama/model_catalog.json` to add or update the metadata for the new model.

---

**Questions? Open an issue or contact your Copilot system admin.**