# This will later handle model metadata enrichment for SaaS (placeholder for now)

# def get_model_info(name):
#     # Simplified example catalog - expand as you pull metadata dynamically later
#     catalog = {
#         "llama3.1:8b": {"ram": "28-32 GB", "reasoning": "🧠🧠🧠🧠🧠", "jetson": "❌ borderline"},
#         "llama3.1:8b-q4_0": {"ram": "~10-12 GB", "reasoning": "🧠🧠🧠🧠🧠", "jetson": "✅ perfect"},
#         "llama3.1:8b-q4_K_M": {"ram": "~8-9 GB", "reasoning": "🧠🧠🧠🧠🧠", "jetson": "✅ ideal"},
#         "llama4:maverick": {"ram": "~4 GB", "reasoning": "🧠🧠", "jetson": "✅ safe"}
#     }
#     return catalog.get(name, {"ram": "-", "reasoning": "-", "jetson": "-"})


# utils/model_catalog_utils.py

def get_model_info(name):
    catalog = {
        "llama3:8b": {
            "ram": "16 GB",
            "reasoning": "Strong general reasoning",
            "jetson": "Safe (if you have enough RAM)"
        },
        "mistral:7b": {
            "ram": "12 GB",
            "reasoning": "High reasoning ability",
            "jetson": "Safe"
        },
        "llama3:latest": {
            "ram": "16 GB",
            "reasoning": "Strong general reasoning",
            "jetson": "Safe"
        },
        "mxbai-embed-large:latest": {
            "ram": "8 GB",
            "reasoning": "Embedding only",
            "jetson": "Safe"
        }
    }
    return catalog.get(name, {"ram": "-", "reasoning": "-", "jetson": "-"})
