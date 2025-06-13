import os

def list_directories(path):
    os.makedirs(path, exist_ok=True)
    return [
        name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    ]
