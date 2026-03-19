import json
import os

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.filename):
            default_settings = {
                "recent_collections": [],
                "hotkeys": {}
            }
            self.save_settings(default_settings)
            return default_settings
            
        with open(self.filename, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if "recent_collections" not in data: data["recent_collections"] = []
                if "hotkeys" not in data: data["hotkeys"] = {}
                return data
            except json.JSONDecodeError:
                return {"recent_collections": [], "hotkeys": {}}

    def save_settings(self, settings=None):
        if settings is not None:
            self.settings = settings
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.settings, file, indent=4, ensure_ascii=False)

    def add_recent_collection(self, collection_name):
        if collection_name in self.settings["recent_collections"]:
            self.settings["recent_collections"].remove(collection_name)
        self.settings["recent_collections"].insert(0, collection_name)
        
        # Giữ lại tối đa 3 collection gần nhất
        if len(self.settings["recent_collections"]) > 3:
            self.settings["recent_collections"] = self.settings["recent_collections"][:3]
            
        self.save_settings()

    def get_recent_collections(self):
        return self.settings.get("recent_collections", [])

    def get_hotkeys(self):
        return self.settings.get("hotkeys", {})

    def set_hotkey(self, collection_name, hotkey):
        if "hotkeys" not in self.settings:
            self.settings["hotkeys"] = {}
        if not hotkey:
            if collection_name in self.settings["hotkeys"]:
                del self.settings["hotkeys"][collection_name]
        else:
            self.settings["hotkeys"][collection_name] = hotkey
        self.save_settings()
        
    def remove_collection_data(self, collection_name):
        if collection_name in self.settings.get("recent_collections", []):
            self.settings["recent_collections"].remove(collection_name)
        if collection_name in self.settings.get("hotkeys", {}):
            del self.settings["hotkeys"][collection_name]
        self.save_settings()