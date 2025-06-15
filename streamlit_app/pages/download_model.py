import streamlit as st
import ollama
import pandas as pd
import utils.model_catalog_utils as model_utils

st.set_page_config(page_title="Jetson Copilot - Model Manager")

st.title("Downloaded Models")

models = ollama.list()["models"]
table = []

for model in models:
    info = model_utils.get_model_info(model['name'])
    table.append({
        "Name": model['name'],
        "Size (MiB)": f"{model['size'] / 1024 / 1024:.1f}",
        "RAM": info['ram'],
        "Reasoning": info['reasoning'],
        "Jetson Safe": info['jetson']
    })

df = pd.DataFrame(table)
st.dataframe(df)

st.page_link("app.py", label="Back to home", icon="🏠")
