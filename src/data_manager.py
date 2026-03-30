import json
import os

class DataManager:
    def __init__(self, filename="bookmarks.json"):
        self.filename = filename

    def load_data(self):
        """Loads data from a JSON file. If the file doesn't exist, returns default data."""
        if not os.path.exists(self.filename):
            # Default data for the first time opening the app
            default_data = {
                "User Guide": [
                    {"note": "Click the + button in the sidebar to create a new Collection", "link": ""},
                    {"note": "Right-click on a Collection to Edit/Delete", "link": ""},
                    {"note": "Click on a Note with a link to open it in the browser", "link": "https://google.com"}
                ]
            }
            self.save_data(default_data)
            return default_data
            
        # If the file exists, read and return the data
        with open(self.filename, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {} # Return an empty dict if the file is corrupted

    def save_data(self, data):
        """Saves the entire data (dictionary) to a JSON file."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            # indent=4 makes the JSON file nicely formatted and human-readable
            # ensure_ascii=False allows saving of non-ASCII characters
            json.dump(data, file, indent=4, ensure_ascii=False)