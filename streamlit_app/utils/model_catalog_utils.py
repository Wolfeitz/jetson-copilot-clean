import os
import json
import ollama
import time

# File locations
CATALOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model_catalog.json')

# Ollama model config
OLLAMA_MODEL = "llama3:8b"

# Load catalog

def load_catalog():
    if not os.path.exists(CATALOG_FILE):
        return {}
    with open(CATALOG_FILE, "r") as f:
        return json.load(f)

# Save catalog

def save_catalog(catalog):
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=2)

# GPT prompt builder

def build_enrichment_prompt(model_name):
    return f"""
You are an expert AI model analyst. Given the following LLM model name:

**Model Name:** {model_name}

Please return an estimated summary of the model's properties in strict JSON format:

{{
  "RAM": "<estimated RAM usage for inference>",
  "Reasoning": "<🧠 level, 1-5 brains>",
  "JetsonSafe": "<✅ or ❌ depending on Jetson Orin AGX compatibility>",
  "Why": "<one sentence explanation of best use case>"
}}

Strictly respond with only valid JSON, no commentary or explanation.
"""

# Local Ollama inference core

def call_gpt(prompt):
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "system", "content": prompt}]
    )
    return response['message']['content']

# Enrichment pipeline

def enrich_model_metadata(model_name):
    prompt = build_enrichment_prompt(model_name)
    print(f"Enriching metadata for model: {model_name}")

    try:
        raw_response = call_gpt(prompt)
        metadata = json.loads(raw_response)
        return metadata
    except Exception as e:
        print(f"Error parsing GPT response for model {model_name}: {e}")
        return {
            "RAM": "Unknown",
            "Reasoning": "-",
            "JetsonSafe": "Unknown",
            "Why": "Unknown"
        }

# Auto-sync from installed Ollama models

def sync_catalog():
    catalog = load_catalog()
    models = ollama.list()["models"]

    for model in models:
        model_name = model['model']  # <-- modernized API fix here
        if model_name not in catalog:
            print(f"Discovered new model: {model_name}")
            enriched = enrich_model_metadata(model_name)
            catalog[model_name] = enriched
            save_catalog(catalog)
            time.sleep(1)

    print("Model catalog sync complete.")
    return catalog

# Metadata retrieval for download_model.py

def get_model_metadata(model_name):
    catalog = load_catalog()
    return catalog.get(model_name, {
        "RAM": "-",
        "Reasoning": "-",
        "JetsonSafe": "-",
        "Why": "-"
    })
