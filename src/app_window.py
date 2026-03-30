from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QFrame, QListWidget, QPushButton, QLabel, QScrollArea,
                               QInputDialog, QMessageBox, QMenu, QSystemTrayIcon, QSplitter)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction

from src.styles import MODERN_STYLE
from src.components import NoteWidget, NoteDialog
from src.data_manager import DataManager # IMPORT FILE MỚI
from src.settings_manager import SettingsManager
from src.tray_manager import TrayManager
from src.hotkey_manager import HotkeyWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Bookmark App")
        self.resize(900, 600)
        self.setStyleSheet(MODERN_STYLE)

        # Initialize Settings Manager
        self.settings_manager = SettingsManager("settings.json")

        # Initialize Data Manager and load data from JSON file
        self.data_manager = DataManager("bookmarks.json")
        self.db = self.data_manager.load_data()
        
        self.current_collection = None

        self.init_ui()
        self.load_collections()
        
        self.tray_manager = TrayManager(self)
        self.tray_manager.show()
        
        self.hotkey_manager = HotkeyWorker(self)
        self.hotkey_manager.hotkey_triggered.connect(self.add_note_from_hotkey)
        self.hotkey_manager.setup_hotkeys()

    def save_current_state(self):
        """Utility function: Call this whenever data changes to save to file."""
        self.data_manager.save_data(self.db)

    def closeEvent(self, event):
        if hasattr(self, 'tray_manager') and self.tray_manager.is_quitting:
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray_manager.showMessage(
                "Running in background",
                "The application has been minimized to the system tray. Click the icon to open it again.",
                QSystemTrayIcon.Information,
                2000
            )

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(2)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #333333; }")
        main_layout.addWidget(self.splitter)

        # --- SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        sidebar_header = QHBoxLayout()
        lbl_logo = QLabel("Collections")
        lbl_logo.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        self.btn_add_collection = QPushButton("+")
        self.btn_add_collection.setObjectName("btn_add_collection")
        self.btn_add_collection.setFixedSize(30, 30)
        self.btn_add_collection.clicked.connect(self.add_collection)
        
        sidebar_header.addWidget(lbl_logo)
        sidebar_header.addStretch()
        sidebar_header.addWidget(self.btn_add_collection)

        self.collection_list = QListWidget()
        self.collection_list.itemClicked.connect(self.on_collection_selected)
        
        self.collection_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.collection_list.customContextMenuRequested.connect(self.show_collection_context_menu)
        
        sidebar_layout.addLayout(sidebar_header)
        sidebar_layout.addWidget(self.collection_list)

        # --- MAIN CONTENT ---
        self.main_content = QFrame()
        self.main_content.setObjectName("main_content")
        content_layout = QVBoxLayout(self.main_content)

        top_bar = QHBoxLayout()
        self.btn_menu = QPushButton("☰")
        self.btn_menu.clicked.connect(self.toggle_menu)
        
        self.lbl_title = QLabel("")
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        
        self.btn_add = QPushButton("+")
        self.btn_add.setObjectName("btn_add")
        self.btn_add.clicked.connect(self.add_note)
        self.btn_add.hide()

        top_bar.addWidget(self.btn_menu)
        top_bar.addWidget(self.lbl_title, 1)
        top_bar.addWidget(self.btn_add)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.notes_layout = QVBoxLayout(self.scroll_content)
        self.notes_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.hide()

        # Label to display in the center when no Collection is selected
        self.lbl_empty = QLabel("Select a Collection...")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.setStyleSheet("color: #888888; font-size: 18px; font-style: italic;")

        content_layout.addLayout(top_bar)
        content_layout.addWidget(self.lbl_empty, 1)
        content_layout.addWidget(self.scroll_area)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_content)
        
        self.splitter.setSizes([200, 700])

        self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.finished.connect(self.on_menu_animation_finished)

    # --- SIDEBAR / MENU LOGIC ---
    def toggle_menu(self):
        start_val = self.sidebar.width()
        if start_val > 0:
            self.sidebar_last_width = start_val
            end_val = 0
        else:
            end_val = getattr(self, 'sidebar_last_width', 200)
            
        self.animation.setStartValue(start_val)
        self.animation.setEndValue(end_val)
        self.animation.start()
        
    def on_menu_animation_finished(self):
        if self.sidebar.width() > 0:
            self.sidebar.setMaximumWidth(16777215)

    def load_collections(self):
        self.collection_list.clear()
        self.collection_list.addItems(self.db.keys())

    def on_collection_selected(self, item):
        self.current_collection = item.text()
        self.lbl_title.setText(self.current_collection)
        self.btn_add.show()
        self.lbl_empty.hide()
        self.scroll_area.show()
        self.render_notes()
        
        self.settings_manager.add_recent_collection(self.current_collection)

    def add_collection(self):
        text, ok = QInputDialog.getText(self, "Add Collection", "Enter new Collection name:")
        if ok and text:
            text = text.strip()
            if text in self.db:
                QMessageBox.warning(self, "Error", "Collection name already exists!")
                return
            self.db[text] = []
            self.save_current_state() # SAVE DATA
            self.load_collections()

    def show_collection_context_menu(self, pos):
        item = self.collection_list.itemAt(pos)
        if not item: return

        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #252525; color: #e0e0e0; border: none; border-radius: 5px; padding: 4px; } QMenu::item { padding: 6px 20px; border-radius: 4px; } QMenu::item:selected { background-color: #444444; color: white; }")
        
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        hotkey_action = QAction("Set Hotkey...", self)
        
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(hotkey_action)

        action = menu.exec(self.collection_list.mapToGlobal(pos))
        
        if action == rename_action:
            self.rename_collection(item)
        elif action == delete_action:
            self.delete_collection(item)
        elif action == hotkey_action:
            self.set_collection_hotkey(item)

    def rename_collection(self, item):
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename Collection", "New name:", text=old_name)
        if ok and new_name:
            new_name = new_name.strip()
            if new_name == old_name: return
            if new_name in self.db:
                QMessageBox.warning(self, "Error", "Collection name already exists!")
                return
            
            self.db[new_name] = self.db.pop(old_name)
            
            if self.current_collection == old_name:
                self.current_collection = new_name
                self.lbl_title.setText(new_name)
            
            recent = self.settings_manager.get_recent_collections()
            if old_name in recent:
                recent[recent.index(old_name)] = new_name
                self.settings_manager.save_settings()
            hotkeys = self.settings_manager.get_hotkeys()
            if old_name in hotkeys:
                hotkeys[new_name] = hotkeys.pop(old_name)
                self.settings_manager.save_settings()
                self.hotkey_manager.setup_hotkeys()
            
            self.save_current_state() # SAVE DATA
            self.load_collections()

    def delete_collection(self, item):
        col_name = item.text()
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f'Are you sure you want to delete the Collection "{col_name}"?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.db[col_name]
            if self.current_collection == col_name:
                self.current_collection = None
                self.lbl_title.setText("")
                self.btn_add.hide()
                self.scroll_area.hide()
                self.lbl_empty.show()
                for i in reversed(range(self.notes_layout.count())): 
                    widget = self.notes_layout.itemAt(i).widget()
                    if widget: widget.deleteLater()
            
            self.settings_manager.remove_collection_data(col_name)
            self.hotkey_manager.setup_hotkeys()
            
            self.save_current_state() # SAVE DATA
            self.load_collections()

    def set_collection_hotkey(self, item):
        col_name = item.text()
        current_hotkey = self.settings_manager.get_hotkeys().get(col_name, "")
        text, ok = QInputDialog.getText(self, "Set Hotkey",
                                        f"Enter hotkey to save selected text to '{col_name}'\n(e.g., ctrl+shift+a, leave empty to clear):",
                                        text=current_hotkey)
        if ok:
            self.settings_manager.set_hotkey(col_name, text.strip())
            self.hotkey_manager.setup_hotkeys()
            if text.strip():
                QMessageBox.information(self, "Success", f"Hotkey '{text.strip()}' set for {col_name}")
            else:
                QMessageBox.information(self, "Success", f"Hotkey for {col_name} has been removed")

    def add_note_from_hotkey(self, collection_name, selected_text):
        if not selected_text: return
        link = ""
        note = selected_text
        if note.startswith("http://") or note.startswith("https://"):
            link = note
            note = "Saved from hotkey"
            
        self.db[collection_name].append({"note": note, "link": link})
        self.save_current_state()
        if self.current_collection == collection_name:
            self.render_notes()
        self.settings_manager.add_recent_collection(collection_name)
        self.tray_manager.showMessage("Note Added", f"Saved selected content to '{collection_name}'", QSystemTrayIcon.Information, 2000)

    # --- NOTES LOGIC ---
    def render_notes(self):
        for i in reversed(range(self.notes_layout.count())): 
            widget = self.notes_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        if self.current_collection and self.current_collection in self.db:
            for index, item in enumerate(self.db[self.current_collection]):
                note_w = NoteWidget(item['note'], item['link'])
                note_w.index_in_db = index
                note_w.deleted.connect(self.delete_note)
                note_w.edited.connect(self.edit_note)
                self.notes_layout.addWidget(note_w)

    def add_note(self):
        dialog = NoteDialog(self)
        if dialog.exec():
            note, link = dialog.get_data()
            if note or link:
                self.db[self.current_collection].append({"note": note, "link": link})
                self.save_current_state() 
                self.render_notes()

    def delete_note(self, widget):
        del self.db[self.current_collection][widget.index_in_db]
        self.save_current_state() 
        self.render_notes()

    def edit_note(self, widget, new_note, new_link):
        self.db[self.current_collection][widget.index_in_db] = {"note": new_note, "link": new_link}
        self.save_current_state() 
        self.render_notes()