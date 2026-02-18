from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QFrame, QListWidget, QPushButton, QLabel, QScrollArea,
                               QInputDialog, QMessageBox, QMenu)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction

from src.styles import MODERN_STYLE
from src.components import NoteWidget, NoteDialog
from src.data_manager import DataManager # IMPORT FILE MỚI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Bookmark App")
        self.resize(900, 600)
        self.setStyleSheet(MODERN_STYLE)

        # Khởi tạo Data Manager và tải dữ liệu từ file JSON
        self.data_manager = DataManager("bookmarks.json")
        self.db = self.data_manager.load_data()
        
        self.current_collection = None

        self.init_ui()
        self.load_collections()

    def save_current_state(self):
        """Hàm tiện ích: Gọi hàm này mỗi khi có thay đổi dữ liệu để lưu vào file."""
        self.data_manager.save_data(self.db)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        sidebar_header = QHBoxLayout()
        lbl_logo = QLabel("📚 Collections")
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
        self.btn_menu = QPushButton("☰ Menu")
        self.btn_menu.clicked.connect(self.toggle_menu)
        
        self.lbl_title = QLabel("Chọn một Collection...")
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.btn_add = QPushButton("+ Thêm Note")
        self.btn_add.setObjectName("btn_add")
        self.btn_add.clicked.connect(self.add_note)
        self.btn_add.hide()

        top_bar.addWidget(self.btn_menu)
        top_bar.addWidget(self.lbl_title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_add)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.notes_layout = QVBoxLayout(self.scroll_content)
        self.notes_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)

        content_layout.addLayout(top_bar)
        content_layout.addWidget(self.scroll_area)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_content)

        self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)

    # --- LOGIC CHO SIDEBAR / MENU ---
    def toggle_menu(self):
        start_val = self.sidebar.width()
        end_val = 0 if start_val > 0 else 200
        self.animation.setStartValue(start_val)
        self.animation.setEndValue(end_val)
        self.animation.start()

    def load_collections(self):
        self.collection_list.clear()
        self.collection_list.addItems(self.db.keys())

    def on_collection_selected(self, item):
        self.current_collection = item.text()
        self.lbl_title.setText(self.current_collection)
        self.btn_add.show()
        self.render_notes()

    # --- LOGIC THÊM, SỬA, XÓA COLLECTION ---
    def add_collection(self):
        text, ok = QInputDialog.getText(self, "Thêm Collection", "Nhập tên Collection mới:")
        if ok and text:
            text = text.strip()
            if text in self.db:
                QMessageBox.warning(self, "Lỗi", "Tên Collection đã tồn tại!")
                return
            self.db[text] = []
            self.save_current_state() # LƯU DATA
            self.load_collections()

    def show_collection_context_menu(self, pos):
        item = self.collection_list.itemAt(pos)
        if not item: return

        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #313244; color: white; border-radius: 5px; } QMenu::item:selected { background-color: #89b4fa; color: black; }")
        
        rename_action = QAction("Đổi tên", self)
        delete_action = QAction("Xóa", self)
        
        menu.addAction(rename_action)
        menu.addAction(delete_action)

        action = menu.exec(self.collection_list.mapToGlobal(pos))
        
        if action == rename_action:
            self.rename_collection(item)
        elif action == delete_action:
            self.delete_collection(item)

    def rename_collection(self, item):
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Đổi tên Collection", "Tên mới:", text=old_name)
        if ok and new_name:
            new_name = new_name.strip()
            if new_name == old_name: return
            if new_name in self.db:
                QMessageBox.warning(self, "Lỗi", "Tên Collection đã tồn tại!")
                return
            
            self.db[new_name] = self.db.pop(old_name)
            
            if self.current_collection == old_name:
                self.current_collection = new_name
                self.lbl_title.setText(new_name)
            
            self.save_current_state() # LƯU DATA
            self.load_collections()

    def delete_collection(self, item):
        col_name = item.text()
        reply = QMessageBox.question(self, 'Xác nhận xóa', 
                                     f'Bạn có chắc muốn xóa Collection "{col_name}"?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.db[col_name]
            if self.current_collection == col_name:
                self.current_collection = None
                self.lbl_title.setText("Chọn một Collection...")
                self.btn_add.hide()
                for i in reversed(range(self.notes_layout.count())): 
                    widget = self.notes_layout.itemAt(i).widget()
                    if widget: widget.deleteLater()
            
            self.save_current_state() # LƯU DATA
            self.load_collections()

    # --- LOGIC CHO NOTES ---
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
                self.save_current_state() # LƯU DATA
                self.render_notes()

    def delete_note(self, widget):
        del self.db[self.current_collection][widget.index_in_db]
        self.save_current_state() # LƯU DATA
        self.render_notes()

    def edit_note(self, widget, new_note, new_link):
        self.db[self.current_collection][widget.index_in_db] = {"note": new_note, "link": new_link}
        self.save_current_state() # LƯU DATA
        self.render_notes()