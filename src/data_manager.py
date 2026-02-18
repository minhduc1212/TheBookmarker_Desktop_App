import json
import os

class DataManager:
    def __init__(self, filename="bookmarks.json"):
        self.filename = filename

    def load_data(self):
        """Đọc dữ liệu từ file JSON. Nếu file chưa tồn tại, trả về data mặc định."""
        if not os.path.exists(self.filename):
            # Dữ liệu mặc định cho lần đầu tiên mở app
            default_data = {
                "Hướng dẫn sử dụng": [
                    {"note": "Bấm dấu + ở Sidebar để tạo Collection mới", "link": ""},
                    {"note": "Chuột phải vào Collection để Sửa/Xóa", "link": ""},
                    {"note": "Bấm vào Note chứa link để mở trình duyệt", "link": "https://google.com"}
                ]
            }
            self.save_data(default_data)
            return default_data
            
        # Nếu file đã tồn tại, đọc và trả về data
        with open(self.filename, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {} # Trả về dict rỗng nếu file lỗi

    def save_data(self, data):
        """Lưu toàn bộ data (dictionary) xuống file JSON."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            # indent=4 giúp file json được format đẹp mắt, dễ đọc bằng mắt thường
            # ensure_ascii=False giúp lưu được tiếng Việt có dấu
            json.dump(data, file, indent=4, ensure_ascii=False)