import keyboard
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication

class HotkeyWorker(QObject):
    execute_copy = Signal(str) # Tín hiệu nội bộ để nhảy sang luồng chính (Main Thread) an toàn
    hotkey_triggered = Signal(str, str) # Phát: tên collection, văn bản được bôi đen

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings_manager = main_window.settings_manager
        self.execute_copy.connect(self.perform_copy)

    def setup_hotkeys(self):
        keyboard.unhook_all()
        hotkeys = self.settings_manager.get_hotkeys()
        for col, hk in hotkeys.items():
            if hk and col in self.main_window.db:
                try:
                    # Đăng ký phím tắt (suppress=False để không chặn các phím khác của hệ thống)
                    keyboard.add_hotkey(hk, self.on_hotkey, args=(col,), suppress=False)
                except Exception as e:
                    print(f"Lỗi đăng ký phím tắt {hk}: {e}")

    def on_hotkey(self, collection_name):
        # Chạy trong luồng riêng của thư viện keyboard, phát tín hiệu về Main Thread
        self.execute_copy.emit(collection_name)

    def perform_copy(self, collection_name):
        clipboard = QApplication.clipboard()
        old_text = clipboard.text()
        
        # Tự động nhấn Ctrl+C để copy văn bản đang bôi đen
        keyboard.send('ctrl+c')
        
        # Đợi 150ms để Clipboard cập nhật xong
        QTimer.singleShot(150, lambda: self.check_clipboard(collection_name, old_text))

    def check_clipboard(self, collection_name, old_text):
        clipboard = QApplication.clipboard()
        new_text = clipboard.text()
        
        if new_text and new_text.strip():
            self.hotkey_triggered.emit(collection_name, new_text.strip())