import os
import sys
import json
import PySide6.QtWidgets as qw
import PySide6.QtCore as qc
import PySide6.QtGui as qg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLLECTIONS_FILE = os.path.join(BASE_DIR, 'collections.json')

class BookmarkApp(qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OwMarker")
        self.resize(900, 600)
        
        self.collections = {}
        self.load_data()
        
        self.setup_ui()
        self.populate_collections()
        
    def setup_ui(self):
        # Main Layout
        main_widget = qw.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = qw.QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter
        splitter = qw.QSplitter(qc.Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- Left Panel (Collections Menu) ---
        left_panel = qw.QWidget()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("background-color: #2c3e50; color: white;")
        left_layout = qw.QVBoxLayout(left_panel)
        
        # Header
        header_label = qw.QLabel("COLLECTIONS")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; color: #ecf0f1;")
        left_layout.addWidget(header_label)
        
        # Collection List
        self.collection_list = qw.QListWidget()
        self.collection_list.setFocusPolicy(qc.Qt.NoFocus)
        self.collection_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:selected {
                background-color: #34495e;
                color: #3498db;
                border-left: 4px solid #3498db;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
        """)
        self.collection_list.currentRowChanged.connect(self.change_collection)
        left_layout.addWidget(self.collection_list)
        
        # Add Collection Button
        add_col_btn = qw.QPushButton("+ New Collection")
        add_col_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        add_col_btn.clicked.connect(self.add_collection)
        left_layout.addWidget(add_col_btn)
        
        splitter.addWidget(left_panel)
        
        # --- Right Panel (Notes) ---
        right_panel = qw.QWidget()
        right_panel.setStyleSheet("background-color: #ecf0f1;")
        right_layout = qw.QVBoxLayout(right_panel)
        
        # Stacked Widget for different collection views
        self.stack = qw.QStackedWidget()
        right_layout.addWidget(self.stack)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 650])
        splitter.setCollapsible(0, False)

    def load_data(self):
        if os.path.exists(COLLECTIONS_FILE):
            try:
                with open(COLLECTIONS_FILE, 'r', encoding='utf-8') as f:
                    self.collections = json.load(f)
            except:
                self.collections = {"General": []}
        else:
            self.collections = {"General": []}
            self.save_data()

    def save_data(self):
        with open(COLLECTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.collections, f, indent=4)

    def populate_collections(self):
        self.collection_list.clear()
        # Clear stack
        for i in range(self.stack.count()):
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
            
        for name in self.collections:
            item = qw.QListWidgetItem(name)
            self.collection_list.addItem(item)
            
            # Create page for this collection
            page = self.create_collection_page(name)
            self.stack.addWidget(page)
            
        if self.collection_list.count() > 0:
            self.collection_list.setCurrentRow(0)

    def create_collection_page(self, name):
        page = qw.QWidget()
        layout = qw.QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = qw.QLabel(name)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Input Area
        input_layout = qw.QHBoxLayout()
        
        note_title = qw.QLineEdit()
        note_title.setPlaceholderText("Note Name")
        note_title.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px;")
        
        note_url = qw.QLineEdit()
        note_url.setPlaceholderText("URL (e.g. https://google.com)")
        note_url.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px;")
        
        add_btn = qw.QPushButton("Add Note")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 8px 15px;
                border: none; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        
        # List of Notes
        notes_list = qw.QListWidget()
        notes_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
                color: #2980b9; /* Link color */
                text-decoration: underline;
            }
            QListWidget::item:hover {
                background-color: #f7f9f9;
                color: #e74c3c;
            }
        """)
        # Populate notes
        for note in self.collections.get(name, []):
            self.add_note_to_list(notes_list, note)
            
        # Connect Add Button
        add_btn.clicked.connect(lambda: self.add_note(name, note_title, note_url, notes_list))
        
        # Connect Click
        notes_list.itemClicked.connect(self.open_note_url)
        
        input_layout.addWidget(note_title)
        input_layout.addWidget(note_url)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        layout.addWidget(notes_list)
        
        return page

    def add_note_to_list(self, list_widget, note_data):
        item = qw.QListWidgetItem(note_data['title'])
        item.setData(qc.Qt.UserRole, note_data['url'])
        item.setToolTip(note_data['url'])
        # Make it look like a link
        font = item.font()
        font.setUnderline(True)
        item.setFont(font)
        list_widget.addItem(item)

    def add_note(self, collection_name, title_edit, url_edit, list_widget):
        title = title_edit.text().strip()
        url = url_edit.text().strip()
        
        if not title:
            qw.QMessageBox.warning(self, "Error", "Title is required!")
            return
            
        if url and not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
            
        note_data = {"title": title, "url": url}
        self.collections[collection_name].append(note_data)
        self.save_data()
        
        self.add_note_to_list(list_widget, note_data)
        title_edit.clear()
        url_edit.clear()

    def open_note_url(self, item):
        url = item.data(qc.Qt.UserRole)
        if url:
            qg.QDesktopServices.openUrl(qc.QUrl(url))

    def add_collection(self):
        text, ok = qw.QInputDialog.getText(self, "New Collection", "Collection Name:")
        if ok and text:
            if text in self.collections:
                qw.QMessageBox.warning(self, "Error", "Collection already exists!")
                return
            self.collections[text] = []
            self.save_data()
            
            # Update UI
            item = qw.QListWidgetItem(text)
            self.collection_list.addItem(item)
            page = self.create_collection_page(text)
            self.stack.addWidget(page)
            self.collection_list.setCurrentRow(self.collection_list.count() - 1)

    def change_collection(self, row):
        self.stack.setCurrentIndex(row)

if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BookmarkApp()
    window.show()
    sys.exit(app.exec())
