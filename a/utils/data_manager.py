import json
import os

DATA_DIR = 'data'

FILES = {
    'users': os.path.join(DATA_DIR, 'users.json'),
    'restaurants': os.path.join(DATA_DIR, 'restaurants.json'),
    'menu_items': os.path.join(DATA_DIR, 'menu_items.json'),
    'orders': os.path.join(DATA_DIR, 'orders.json')
}

def _ensure_file_exists(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_data(key):
    filepath = FILES.get(key)
    if not filepath:
        raise ValueError(f"Unknown data key: {key}")
    
    _ensure_file_exists(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(key, data):
    filepath = FILES.get(key)
    if not filepath:
        raise ValueError(f"Unknown data key: {key}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_next_id(data_list):
    if not data_list:
        return 1
    return max(item.get('id', 0) for item in data_list) + 1
