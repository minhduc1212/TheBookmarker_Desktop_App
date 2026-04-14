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
                "User Guide": {
                    "description": "Basic usage instructions.",
                    "notes": [
                        {
                            "name": "Create Collection",
                            "description": "Click the + button in the sidebar to create a new Collection.",
                            "links": []
                        },
                        {
                            "name": "Manage Collection",
                            "description": "Right-click on a Collection to edit description, rename, or delete.",
                            "links": []
                        },
                        {
                            "name": "Open Links",
                            "description": "Click on a note to open its first link in the browser.",
                            "links": ["https://google.com"]
                        }
                    ]
                }
            }
            self.save_data(default_data)
            return default_data
            
        # If the file exists, read and return the data
        with open(self.filename, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                normalized_data = self._normalize_data(data)
                if normalized_data != data:
                    self.save_data(normalized_data)
                return normalized_data
            except json.JSONDecodeError:
                return {} # Return an empty dict if the file is corrupted

    def save_data(self, data):
        """Saves the entire data (dictionary) to a JSON file."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            # indent=4 makes the JSON file nicely formatted and human-readable
            # ensure_ascii=False allows saving of non-ASCII characters
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _normalize_data(self, data):
        """Migrates older data formats to the current schema."""
        if not isinstance(data, dict):
            return {}

        normalized = {}
        for collection_name, collection_value in data.items():
            if isinstance(collection_value, list):
                notes = [self._normalize_note_item(note_item) for note_item in collection_value]
                normalized[collection_name] = {
                    "description": "",
                    "notes": notes
                }
                continue

            if isinstance(collection_value, dict):
                raw_notes = collection_value.get("notes", [])
                if not isinstance(raw_notes, list):
                    raw_notes = []
                notes = [self._normalize_note_item(note_item) for note_item in raw_notes]
                normalized[collection_name] = {
                    "description": str(collection_value.get("description", "")).strip(),
                    "notes": notes
                }
                continue

            normalized[collection_name] = {"description": "", "notes": []}

        return normalized

    def _normalize_note_item(self, note_item):
        """Normalizes a note object to {name, description, links} schema."""
        if not isinstance(note_item, dict):
            return {"name": "", "description": "", "links": []}

        if "name" in note_item or "description" in note_item or "links" in note_item:
            links = note_item.get("links", [])
            if isinstance(links, str):
                links = [links] if links.strip() else []
            if not isinstance(links, list):
                links = []
            links = [str(link).strip() for link in links if str(link).strip()]
            return {
                "name": str(note_item.get("name", "")).strip(),
                "description": str(note_item.get("description", "")).strip(),
                "links": links
            }

        legacy_note = str(note_item.get("note", "")).strip()
        legacy_link = str(note_item.get("link", "")).strip()
        return {
            "name": legacy_note,
            "description": "",
            "links": [legacy_link] if legacy_link else []
        }