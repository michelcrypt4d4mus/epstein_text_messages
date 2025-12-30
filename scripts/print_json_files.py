import json

from dotenv import load_dotenv
from rich.panel import Panel
load_dotenv()

from epstein_files.util.file_helper import JSON_DIR
from epstein_files.util.rich import console


for file in [f for f in JSON_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]:
    console.print('\n', Panel(file.name, expand=False))

    with open(file, encoding='utf-8-sig') as f:
        json_data = json.load(f)
        console.print_json(json.dumps(json_data))
