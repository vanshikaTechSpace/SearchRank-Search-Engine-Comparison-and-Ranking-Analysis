import os
import json
import glob
import logging

def read_queries_set(file_path: str) -> list:
    """
    Reads a list of queries from a text file.
    """
    if not os.path.exists(file_path):
        logging.warning(f"Query file not found at {file_path}. Using default query.")
        return ["important facts on the respiratory system"]

    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def add_query_result(output_dir: str, engine: str, query: str, result: list):
    """
    Saves the search results for a query to a JSON file.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{engine}_Results.json")

    data = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}

    data[query] = result
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def get_latest_results_dir(base_dir: str) -> str:
    """
    Finds the most recently modified subdirectory in the given base directory.
    """
    if not os.path.exists(base_dir): return None
    subdirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if
               os.path.isdir(os.path.join(base_dir, d))]
    return max(subdirs, key=os.path.getmtime) if subdirs else None

def load_results(directory: str, engine: str) -> dict:
    """
    Loads the search results for a specific engine from the given directory.
    """
    pattern = os.path.join(directory, f"{engine}_Result*.json")
    files = glob.glob(pattern)
    if not files: return {}
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)
