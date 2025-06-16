import streamlit as st
import ollama
import pandas as pd
import utils.model_catalog_utils as model_utils

st.set_page_config(page_title="Jetson Copilot - Model Manager")

st.title("Downloaded Models")

models = ollama.list()  # In ollama >=0.5.1, returns list of model names directly
table = []

# for model_name in models:
#     info = model_utils.get_model_info(model_name)
#     model_info = ollama.show(model_name)
#     size_mb = model_info.get('size', 0) / 1024 / 1024  # Safely fallback if size missing

#     table.append({
#         "Name": model_name,
#         "Size (MiB)": f"{size_mb:.1f}",
#         "RAM": info.get('ram', 'N/A'),
#         "Reasoning": info.get('reasoning', 'N/A'),
#         "Jetson Safe": info.get('jetson', 'N/A')
#     })

models = ollama.list()

for model_name in models:
    info = model_utils.get_model_info(model_name)
    table.append({
        "Name": model_name,
        "RAM": info['ram'],
        "Reasoning": info['reasoning'],
        "Jetson Safe": info['jetson']
    })


df = pd.DataFrame(table)
st.dataframe(df)

st.page_link("app.py", label="Back to home", icon="🏠")
