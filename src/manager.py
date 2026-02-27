import json
class BookmarkManager:
    def __init__(self, collection: dict, notes: dict):
        self.collection = collection
        self.notes = notes
        self.load_all_bookmarks()
    def load_all_bookmarks(self):
        with open("bookmarks.json", "r") as f:
            json.load(f)
            