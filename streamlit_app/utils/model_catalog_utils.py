# This will later handle model metadata enrichment for SaaS (placeholder for now)

def get_model_info(name):
    # Simplified example catalog - expand as you pull metadata dynamically later
    catalog = {
        "llama3.1:8b": {"ram": "28-32 GB", "reasoning": "🧠🧠🧠🧠🧠", "jetson": "❌ borderline"},
        "llama3.1:8b-q4_0": {"ram": "~10-12 GB", "reasoning": "🧠🧠🧠🧠🧠", "jetson": "✅ perfect"},
        "llama3.1:8b-q4_K_M": {"ram": "~8-9 GB", "reasoning": "🧠🧠🧠🧠🧠", "jetson": "✅ ideal"},
        "llama4:maverick": {"ram": "~4 GB", "reasoning": "🧠🧠", "jetson": "✅ safe"}
    }
    return catalog.get(name, {"ram": "-", "reasoning": "-", "jetson": "-"})
