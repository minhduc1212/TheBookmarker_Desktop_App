import keyboard
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication

class HotkeyWorker(QObject):
    execute_copy = Signal(str) # Internal signal to safely switch to the main thread
    hotkey_triggered = Signal(str, str) # Emits: collection name, highlighted text

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
                    # Register hotkey (suppress=False to not block other system keys)
                    keyboard.add_hotkey(hk, self.on_hotkey, args=(col,), suppress=False)
                except Exception as e:
                    print(f"Error registering hotkey {hk}: {e}")

    def on_hotkey(self, collection_name):
        # Runs in the keyboard library's own thread, emits a signal to the Main Thread
        self.execute_copy.emit(collection_name)

    def perform_copy(self, collection_name):
        clipboard = QApplication.clipboard()
        old_text = clipboard.text()
        
        # Automatically press Ctrl+C to copy the highlighted text
        keyboard.send('ctrl+c')
        
        # Wait 150ms for the Clipboard to finish updating
        QTimer.singleShot(150, lambda: self.check_clipboard(collection_name, old_text))

    def check_clipboard(self, collection_name, old_text):
        clipboard = QApplication.clipboard()
        new_text = clipboard.text()
        
        if new_text and new_text.strip():
            self.hotkey_triggered.emit(collection_name, new_text.strip())