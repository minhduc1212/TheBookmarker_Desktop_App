from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QFrame, QListWidget, QPushButton, QLabel, QScrollArea)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from src.styles import MODERN_STYLE
from src.components import NoteWidget, NoteDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Bookmark App")
        self.resize(900, 600)
        self.setStyleSheet(MODERN_STYLE)

        # Dữ liệu giả lập (Data MOCK)
        self.db = {
            "Python PySide6": [{"note": "Tài liệu trang chủ", "link": "https://doc.qt.io/"}, {"note": "Chỉ có note, không link", "link": ""}],
            "Công cụ": [{"note": "", "link": "https://github.com"}],
            "Ý tưởng cá nhân": []
        }
        self.current_collection = None

        self.init_ui()
        self.load_collections()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(200) # Độ rộng tối đa khi mở menu
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        lbl_logo = QLabel("📚 Collections")
        lbl_logo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.collection_list = QListWidget()
        self.collection_list.itemClicked.connect(self.on_collection_selected)
        
        sidebar_layout.addWidget(lbl_logo)
        sidebar_layout.addWidget(self.collection_list)

        # --- MAIN CONTENT ---
        self.main_content = QFrame()
        self.main_content.setObjectName("main_content")
        content_layout = QVBoxLayout(self.main_content)

        # Top Bar
        top_bar = QHBoxLayout()
        self.btn_menu = QPushButton("☰ Menu")
        self.btn_menu.clicked.connect(self.toggle_menu)
        
        self.lbl_title = QLabel("Chọn một Collection...")
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.btn_add = QPushButton("+ Thêm Note")
        self.btn_add.setObjectName("btn_add")
        self.btn_add.clicked.connect(self.add_note)
        self.btn_add.hide() # Ẩn nút Add khi chưa chọn Collection

        top_bar.addWidget(self.btn_menu)
        top_bar.addWidget(self.lbl_title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_add)

        # Khu vực Scroll chứa các Note
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.notes_layout = QVBoxLayout(self.scroll_content)
        self.notes_layout.setAlignment(Qt.AlignTop) # Đẩy các note lên trên cùng
        self.scroll_area.setWidget(self.scroll_content)

        content_layout.addLayout(top_bar)
        content_layout.addWidget(self.scroll_area)

        # Lắp ráp vào main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_content)

        # --- ANIMATION TRƯỢT MENU ---
        self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.animation.setDuration(300) # Thời gian trượt (ms)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)

    def toggle_menu(self):
        # Nếu sidebar đang mở (200) thì thu về 0, và ngược lại
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

    def render_notes(self):
        # Xóa các note cũ trên màn hình
        for i in reversed(range(self.notes_layout.count())): 
            widget = self.notes_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        # Render note mới từ DB
        if self.current_collection:
            for index, item in enumerate(self.db[self.current_collection]):
                note_w = NoteWidget(item['note'], item['link'])
                note_w.index_in_db = index # Lưu index để dễ xóa/sửa
                note_w.deleted.connect(self.delete_note)
                note_w.edited.connect(self.edit_note)
                self.notes_layout.addWidget(note_w)

    def add_note(self):
        dialog = NoteDialog(self)
        if dialog.exec():
            note, link = dialog.get_data()
            if note or link: # Chỉ thêm nếu 1 trong 2 có dữ liệu
                self.db[self.current_collection].append({"note": note, "link": link})
                self.render_notes()

    def delete_note(self, widget):
        del self.db[self.current_collection][widget.index_in_db]
        self.render_notes()

    def edit_note(self, widget, new_note, new_link):
        self.db[self.current_collection][widget.index_in_db] = {"note": new_note, "link": new_link}
        self.render_notes()