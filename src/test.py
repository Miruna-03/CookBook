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

def test_json_structure():
    file_path = r"C:\Users\Mirunalini\OneDrive\Desktop\Securin_Assesment\src\US_recipes_null.json"
    data = load_json(file_path)
    
    if data is None:
        print("Failed to load JSON")
        return
    
    print(f"Data type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Number of recipes: {len(data)}")
        print(f"Dictionary keys (first 5): {list(data.keys())[:5]}")
        
        # Check first recipe
        first_key = list(data.keys())[0]
        first_recipe = data[first_key]
        print(f"\nFirst key: {first_key}")
        print(f"First recipe type: {type(first_recipe)}")
        print(f"First recipe keys: {list(first_recipe.keys())}")
        
        # Show sample data
        print("\n=== FIRST RECIPE SAMPLE ===")
        print(f"Title: {first_recipe.get('title')}")
        print(f"Cuisine: {first_recipe.get('cuisine')}")
        print(f"Rating: {first_recipe.get('rating')}")
        print(f"Prep time: {first_recipe.get('prep_time')}")
        print(f"Cook time: {first_recipe.get('cook_time')}")
        
    elif isinstance(data, list):
        print(f"Number of recipes: {len(data)}")
        if len(data) > 0:
            print(f"First recipe keys: {list(data[0].keys())}")
    
    return data

# Call the test function
if __name__ == "__main__":
    test_json_structure()