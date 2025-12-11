import json
import os


def load_json(file_path):
    
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding="utf-8") as file:
            return json.load(file)

    except Exception as e:
        print(f"[ERROR] Could not read JSON: {e}")
        return None

