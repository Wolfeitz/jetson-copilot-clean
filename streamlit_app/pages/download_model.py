import ollama
import streamlit as st
import pandas as pd
import time
import os
import logging
import sys

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Local imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import utils.func
import utils.constants as const
from utils import model_catalog_utils

# Streamlit setup
st.set_page_config(page_title="Jetson Copilot - Download Model", menu_items=None)

# --- DELETE FUNCTION ---
def delete_model(model_name):
    try:
        ollama.delete(model_name)
        st.success(f"Deleted model: {model_name}")
        st.experimental_rerun()
    except Exception as e:
        logging.error(f"Error deleting model: {e}")
        st.error(f"Failed to delete model {model_name}: {e}")

# --- AUTO SYNC CATALOG BEFORE DISPLAY ---
model_catalog_utils.sync_catalog()

# --- DISPLAY MODELS ---
st.subheader("Models Installed on Jetson Copilot")

with st.spinner('Reading models from Ollama...'):
    models = ollama.list()["models"]
    models_data = []

    for model in models:
        name = model['name']
        size_mib = model['size'] / 1024 / 1024
        meta = model_catalog_utils.get_model_metadata(name)

        models_data.append((
            name,
            size_mib,
            meta.get('RAM', '-'),
            meta.get('Reasoning', '-'),
            meta.get('JetsonSafe', '-'),
            meta.get('Why', '-')
        ))

    df = pd.DataFrame(models_data, columns=[
        'Name', 'Size(MiB)', 'RAM', 'Reasoning', 'JetsonSafe', 'Why'
    ])

    if len(models) > 0:
        for i, row in df.iterrows():
            cols = st.columns([5, 1])
            with cols[0]:
                st.write(
                    f"**{row['Name']}** ({row['Size(MiB)']:.1f} MiB)  \n"
                    f"RAM: {row['RAM']}, Reasoning: {row['Reasoning']}, Jetson: {row['JetsonSafe']}  \n"
                    f"_Why:_ {row['Why']}"
                )
            with cols[1]:
                if st.button("❌", key=f"delete_{i}"):
                    delete_model(row['Name'])

# --- DOWNLOAD NEW MODEL SECTION ---
st.subheader("Download a New Model")
st.info("Use model names directly from [Ollama Library](https://ollama.com/library)", icon=":material/info:")

def on_newmodel_name_change():
    newmodel_name = st.session_state.my_newmodel_name
    st.session_state.download_model_disabled = not newmodel_name.strip()

def download_model():
    newmodel_name = st.session_state.my_newmodel_name
    with container_status:
        my_bar = st.progress(0, text="Starting download...")
        try:
            for res in ollama.pull(newmodel_name, stream=True):
                if 'total' in res and 'completed' in res:
                    percent = res['completed'] / res['total']
                    my_bar.progress(percent, text=f"Downloading...")
                else:
                    my_bar.progress(100, text=f"{res['status']}")
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            st.error(f"Download failed: {e}", icon="🚨")
        st.experimental_rerun()

model_name = st.text_input(
    "Model Name",
    key='my_newmodel_name', 
    on_change=on_newmodel_name_change
)
st.button(
    "Download Model", 
    key='my_button', 
    on_click=download_model, 
    disabled=st.session_state.get("download_model_disabled", True)
)
container_status = st.container()

st.page_link("app.py", label="Back to home", icon="🏠")
