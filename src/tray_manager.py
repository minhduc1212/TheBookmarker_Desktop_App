from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle
from PySide6.QtGui import QAction
from src.components import NoteDialog

class TrayManager(QSystemTrayIcon):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.settings_manager = main_window.settings_manager
        self.is_quitting = False
        
        # Sử dụng icon mặc định của hệ thống cho Tray Icon
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setIcon(icon)
        self.setToolTip("Modern Bookmark App")
        
        self.menu = QMenu()
        self.menu.aboutToShow.connect(self.build_menu)
        self.setContextMenu(self.menu)
        
        self.activated.connect(self.on_tray_activated)
        
    def build_menu(self):
        self.menu.clear()
        
        show_action = QAction("Hiển thị ứng dụng", self.menu)
        show_action.triggered.connect(self.show_main_window)
        self.menu.addAction(show_action)
        
        self.menu.addSeparator()
        
        add_col_action = QAction("Thêm Collection mới...", self.menu)
        add_col_action.triggered.connect(self.main_window.add_collection)
        self.menu.addAction(add_col_action)
        
        self.menu.addSeparator()
        
        recent = self.settings_manager.get_recent_collections()
        if recent:
            for col in recent:
                if col in self.main_window.db:
                    action = QAction(f"Thêm Note vào '{col}'", self.menu)
                    action.triggered.connect(lambda checked=False, c=col: self.add_note_to_collection(c))
                    self.menu.addAction(action)
            self.menu.addSeparator()
        
        quit_action = QAction("Thoát", self.menu)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)

    def show_main_window(self):
        self.main_window.showNormal()
        self.main_window.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.show_main_window()

    def add_note_to_collection(self, collection_name):
        dialog = NoteDialog()
        if dialog.exec():
            note, link = dialog.get_data()
            if note or link:
                self.main_window.db[collection_name].append({"note": note, "link": link})
                self.main_window.save_current_state()
                if self.main_window.current_collection == collection_name:
                    self.main_window.render_notes()

    def quit_app(self):
        self.is_quitting = True
        QApplication.quit()