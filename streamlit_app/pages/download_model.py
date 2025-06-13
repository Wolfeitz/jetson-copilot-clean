import ollama
import streamlit as st
import pandas as pd
import time
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
import utils.func 
import utils.constants as const

st.set_page_config(page_title="Jetson Copilot - Download Model", menu_items=None)

# Delete function
def delete_model(model_name):
    try:
        ollama.delete(model_name)
        st.success(f"Deleted model: {model_name}")
        st.experimental_rerun()  # Refresh page after delete
    except Exception as e:
        logging.error(f"Error deleting model: {e}")
        st.error(f"Failed to delete model {model_name}: {e}")

# Display current models
st.subheader("List of Models Already Downloaded")

with st.spinner('Checking existing models hosted on Ollama...'):
    models = ollama.list()["models"]
    models_data = []
    for model in models:
        models_data.append((
            model['name'],
            model['size'] / 1024 / 1024,
            model['details']['format'],
            model['details']['family'],
            model['details']['parameter_size'],
            model['details']['quantization_level']
        ))
    logging.info(f"{len(models)} models found!")
    df = pd.DataFrame(models_data, columns=[
        'Name', 'Size(MiB)', 'Format', 'Family', 'Parameter', 'Quantization'
    ])

    if len(models) != 0:
        for i, row in df.iterrows():
            cols = st.columns([4, 1])
            with cols[0]:
                st.write(f"**{row['Name']}** ({row['Size(MiB)']:.1f} MiB)")
            with cols[1]:
                if st.button("❌", key=f"delete_{i}"):
                    delete_model(row['Name'])

# Download model form
st.subheader("Download a New Model")
st.info("Check the model name on [Ollama Library](https://ollama.com/library) page.", icon=":material/info:")

def on_newmodel_name_change():
    newmodel_name = st.session_state.my_newmodel_name
    st.session_state.download_model_disabled = not newmodel_name.strip()

def download_model():
    newmodel_name = st.session_state.my_newmodel_name
    with container_status:
        start_time = time.time()
        my_bar = st.progress(0, text="progress text")
        try:
            for res in ollama.pull(newmodel_name, stream=True):
                if 'total' in res and 'completed' in res:
                    total = res['total']
                    completed = res['completed']
                    total_in_mib = total / 1024 / 1024
                    completed_in_mib = completed / 1024 / 1024
                    percent = completed / total
                    my_bar.progress(percent, text=f"Downloading ({completed_in_mib:.1f} MiB / {total_in_mib:.1f} MiB)")
                else:
                    my_bar.progress(100, text=f"{res['status']}")
        except ollama.ResponseError as e:
            logging.error(f"A ResponseError occurred: {e}")
            st.error(f"It looks like \"**`{newmodel_name}`**\" is not the right name.", icon="🚨")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            st.error(f"Some other error happened : {e}", icon="🚨")

model_name = st.text_input(
    "Name of model to download",
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
