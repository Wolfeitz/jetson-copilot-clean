import streamlit as st
import ollama
import pandas as pd
import json
import os

st.set_page_config(page_title="Jetson Copilot - Model Catalog", page_icon="🧠")

st.title("Available Models on Host")

# Path to the model catalog
CATALOG_PATH = os.getenv("MODEL_CATALOG_PATH", "/app/model_catalog.json")

# Load model catalog
def load_model_catalog():
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    else:
        st.warning("Model catalog not found. Showing basic model info only.")
        return {}

catalog = load_model_catalog()

# Get models from Ollama host API
try:
    models_resp = ollama.list()
    models_list = models_resp.get("models", [])
except Exception as e:
    st.error(f"Failed to query Ollama on host: {e}")
    models_list = []

table = []
for model_entry in models_list:
    # Handle both 'name' and 'model' keys (Ollama API variants)
    model_name = model_entry.get("name") or model_entry.get("model")
    cat_info = catalog.get(model_name, {})

    size_mb = model_entry.get('size', 0) / (1024*1024)
    ram = cat_info.get("RAM", "N/A")
    reasoning = cat_info.get("Reasoning", "N/A")
    jetson_safe = cat_info.get("JetsonSafe", "N/A")
    why = cat_info.get("Why", "")

    table.append({
        "Model": model_name,
        "Size (MiB)": f"{size_mb:.1f}",
        "RAM": ram,
        "Reasoning": reasoning,
        "Jetson Safe": jetson_safe,
        "Why Choose": why,
    })

if table:
    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No models found on Ollama host.")

# Usage instructions
st.markdown("---")
st.markdown("""
### ℹ️ How to Add New Models

- **On Jetson / Single GPU Systems:**  
    1. Log into the host terminal.
    2. Run:  
       ```shell
       ollama pull <model-name>
       ```
    3. The new model will appear in this list automatically.

- **On DGX or Multi-Container Systems:**  
    1. Enter the Ollama container shell:  
       ```shell
       docker exec -it <ollama-container-name> bash
       ```
    2. Run:  
       ```shell
       ollama pull <model-name>
       ```
    3. Or, mount a shared models volume when launching the container.

- **To update model metadata** (RAM, Jetson safety, etc.),  
    - Edit `model_catalog.json` on the host.
    - **No need to rebuild the app container!**

---

> If you need help or want to request a model for deployment, contact your system administrator or support team.
""")

st.page_link("app.py", label="⬅️ Back to Home", icon="🏠")
