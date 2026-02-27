import sys
import json
import os
from PyQt5.QtWidgets import ( # type: ignore
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSystemTrayIcon, QMenu, QAction, QMessageBox,
    QLabel, QSizePolicy, QTabWidget, QStyle, QInputDialog, QSplitter, QListWidget, QStackedWidget
)
from PyQt5.QtGui import QIcon, QDesktopServices, QMouseEvent # type: ignore
from PyQt5.QtCore import QUrl, Qt, QPoint, pyqtSignal # type: ignore

# --- Configuration ---
COLLECTIONS_FILE = 'collections.json' # JSON file to store all data
APP_ICON_PATH = 'assets/icon.png' 
MINIMIZE_ICON_PATH = 'assets/minimize_icon.png'
MAXIMIZE_ICON_PATH = 'assets/maximize_icon.png'
RESTORE_ICON_PATH = 'assets/restore_icon.png'
CLOSE_ICON_PATH = 'assets/close_icon.png'


# --- Custom Title Bar Widget ---
class CustomTitleBar(QWidget):
    minimize_requested = pyqtSignal()
    maximize_restore_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(40)
        self.dragging = False
        self.offset = QPoint()

        self.setup_ui()
        self.setup_connections()
        self.apply_styles()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if os.path.exists(APP_ICON_PATH):
            self.app_icon_label = QLabel()
            self.app_icon_label.setPixmap(QIcon(APP_ICON_PATH).pixmap(24, 24))
            self.app_icon_label.setContentsMargins(10, 0, 0, 0)
            layout.addWidget(self.app_icon_label)
        else:
            self.app_icon_label = None

        self.title_label = QLabel("OwMarker")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if self.app_icon_label is None:
            self.title_label.setContentsMargins(10, 0, 0, 0)
        else:
            self.title_label.setContentsMargins(5, 0, 0, 0)
        
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.min_btn = QPushButton()
        self.max_res_btn = QPushButton()
        self.close_btn = QPushButton()

        self.min_btn.setFixedSize(40, 40)
        self.max_res_btn.setFixedSize(40, 40)
        self.close_btn.setFixedSize(40, 40)

        self._set_button_icon(self.min_btn, MINIMIZE_ICON_PATH, QStyle.SP_TitleBarMinButton)
        self._set_button_icon(self.close_btn, CLOSE_ICON_PATH, QStyle.SP_TitleBarCloseButton)
        
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_res_btn)
        layout.addWidget(self.close_btn)

    def _set_button_icon(self, button, custom_path, fallback_standard_pixmap):
        if os.path.exists(custom_path):
            button.setIcon(QIcon(custom_path))
        else:
            button.setIcon(self.style().standardIcon(fallback_standard_pixmap))

    def setup_connections(self):
        self.min_btn.clicked.connect(self.minimize_requested.emit)
        self.max_res_btn.clicked.connect(self.maximize_restore_requested.emit)
        self.close_btn.clicked.connect(self.close_requested.emit)

    def apply_styles(self):
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333333;
            }
            CustomTitleBar QLabel {
                color: #f0f0f0;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 16px;
                font-weight: 500;
            }
            CustomTitleBar QPushButton {
                background-color: transparent;
                border: none;
                color: #f0f0f0;
                font-size: 18px;
            }
            CustomTitleBar QPushButton:hover {
                background-color: #333333;
            }
            CustomTitleBar QPushButton#close_btn:hover {
                background-color: #e81123;
            }
            CustomTitleBar QPushButton:pressed {
                background-color: #007acc;
            }
            CustomTitleBar QPushButton#close_btn:pressed {
                background-color: #8c0000;
            }
        """)
        self.min_btn.setObjectName("min_btn")
        self.max_res_btn.setObjectName("max_res_btn")
        self.close_btn.setObjectName("close_btn")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.parent_window.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.maximize_restore_requested.emit()
            event.accept()

    def update_max_restore_icon(self, is_maximized):
        if is_maximized:
            self._set_button_icon(self.max_res_btn, RESTORE_ICON_PATH, QStyle.SP_TitleBarMaxButton)
        else:
            self._set_button_icon(self.max_res_btn, MAXIMIZE_ICON_PATH, QStyle.SP_TitleBarMaxButton)


#Main Window
class BookmarkManagerApp(QMainWindow):
    show_window_and_add_note_signal = pyqtSignal()
    show_window_and_add_collection_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.collections_data = {} 
        self.collection_widgets = {} 

        self.load_collections()

        self.init_ui()
        self.init_tray_icon()
        self.apply_modern_theme() # <-- apply_modern_theme() is called here
        self.populate_all_collection_pages()
        
        self.title_bar.update_max_restore_icon(self.isMaximized()) 

    def init_ui(self):
        self.setWindowTitle('OwMarker')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 900, 700)

        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(1, 1, 1, 1) 
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.title_bar.minimize_requested.connect(self.showMinimized)
        self.title_bar.maximize_restore_requested.connect(self.toggle_maximize_restore)
        self.title_bar.close_requested.connect(self.close)
        main_layout.addWidget(self.title_bar)

        # Main content splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setObjectName("main_splitter")
        main_layout.addWidget(main_splitter)

        # Left panel for collections
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(10, 10, 5, 10)
        left_panel_layout.setSpacing(10)

        collection_list_label = QLabel("COLLECTIONS")
        collection_list_label.setObjectName("collection_list_label")
        self.collection_list_widget = QListWidget()
        self.collection_list_widget.setObjectName("collection_list_widget")

        self.add_collection_button = QPushButton("+ Add Collection")
        self.add_collection_button.setObjectName("add_collection_button")
        self.add_collection_button.clicked.connect(self.prompt_new_collection)

        left_panel_layout.addWidget(collection_list_label)
        left_panel_layout.addWidget(self.collection_list_widget)
        left_panel_layout.addWidget(self.add_collection_button)

        # Right panel for notes (stacked widget)
        self.stacked_widget = QStackedWidget()

        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.stacked_widget)
        main_splitter.setSizes([200, 700]) # Initial sizes

        self.setCentralWidget(main_widget)
        
        self.init_collection_views() 
        self.collection_list_widget.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        self.show_window_and_add_note_signal.connect(self.prompt_add_note)
        self.show_window_and_add_collection_signal.connect(self.prompt_new_collection)

    def apply_modern_theme(self):
        """Apply a modern dark theme to the entire application."""
        self.setStyleSheet("""
            /* Global Styles */
            QMainWindow {
                background-color: #252526; /* Main background */
                border: 1px solid #3c3c3c; /* Subtle border for frameless window */
                border-radius: 8px; /* Rounded corners for the whole window */
            }
            QWidget {
                background-color: #252526;
                color: #cccccc; /* Default text color */
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
            }

            /* QLineEdit - Input Fields */
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
                color: #f0f0f0;
                selection-background-color: #007ACC;
            }
            QLineEdit:focus {
                border: 1px solid #007ACC; /* Highlight on focus */
                background-color: #444444;
            }

            /* QPushButton */
            QPushButton {
                background-color: #007ACC;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 10px 18px;
                font-weight: 600; /* Semi-bold */
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #006BB8;
            }
            QPushButton:pressed {
                background-color: #005A99;
            }
            /* Specific delete button style */
            QPushButton#delete_button { /* Apply to buttons with objectName "delete_button" */
                background-color: #CC293D; /* Red for delete */
            }
            QPushButton#delete_button:hover {
                background-color: #A6202F;
            }
            QPushButton#delete_button:pressed {
                background-color: #801825;
            }

            /* Add Collection Button */
            QPushButton#add_collection_button {
                background-color: #4CAF50; /* Green color for add collection */
                color: white;
                padding: 8px 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                text-transform: none; /* No uppercase */
                letter-spacing: normal;
            }
            QPushButton#add_collection_button:hover {
                background-color: #45a049;
            }
            QPushButton#add_collection_button:pressed {
                background-color: #3e8e41;
            }
            
            /* QListWidget - Collections List */
            QListWidget#collection_list_widget {
                background-color: #2D2D30;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget#collection_list_widget::item {
                padding: 12px 10px;
                border-radius: 4px;
                color: #cccccc;
            }
            QListWidget#collection_list_widget::item:hover {
                background-color: #3c3c3c;
            }
            QListWidget#collection_list_widget::item:selected {
                background-color: #007ACC;
                color: white;
                font-weight: 600;
            }
            
            /* QTableWidget - Data Display */
            QTableWidget {
                background-color: #2D2D30; /* Slightly different background for table */
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                gridline-color: #444444;
                color: #cccccc;
                selection-background-color: #007ACC; /* Blue selection */
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #007ACC;
                color: white;
            }
            QTableWidget QHeaderView::section {
                background-color: #3C3C3C;
                color: #f0f0f0;
                padding: 8px;
                border: 1px solid #333333;
                border-bottom: 2px solid #007ACC; /* Accent border */
                font-weight: 600;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #3C3C3C;
                border: 1px solid #333333;
            }
            /* Scroll bars */
            QScrollBar:vertical, QScrollBar:horizontal {
                border: none;
                background: #3c3c3c;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }

            /* Collection Page Content */
            QWidget[objectName^="collection_page_content_"] {
                padding: 15px;
            }

            QLabel#collection_list_label {
                font-weight: bold;
                color: #007ACC;
                font-size: 14px;
                padding-left: 5px;
                text-transform: uppercase;
            }
        """)
       


    def init_collection_views(self):
        """Initializes the collection list and pages."""
        self.collection_list_widget.clear()
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        self.collection_widgets.clear()

        if not self.collections_data:
            self.collections_data["General"] = []
            self.save_collections()

        for collection_name in sorted(self.collections_data.keys()):
            self._create_and_add_collection_page(collection_name)
        
        if self.collection_list_widget.count() > 0:
            self.collection_list_widget.setCurrentRow(0)

    def _create_and_add_collection_page(self, collection_name):
        """Creates the widget for a single collection's content and adds it to the UI."""
        page_content_widget = QWidget()
        page_content_widget.setObjectName(f"collection_page_content_{collection_name.replace(' ', '_')}") 
        page_layout = QVBoxLayout(page_content_widget)
        page_layout.setContentsMargins(10, 10, 10, 10)
        page_layout.setSpacing(10)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        title_input = QLineEdit()
        title_input.setPlaceholderText("Note Title")
        url_input = QLineEdit()
        url_input.setPlaceholderText("Note URL (e.g., https://example.com)")
        add_button = QPushButton("ADD NOTE")
        
        add_button.clicked.connect(
            lambda checked, col=collection_name, t_input=title_input, u_input=url_input: 
            self.add_note_to_collection(col, t_input, u_input)
        )

        input_layout.addWidget(title_input)
        input_layout.addWidget(url_input)
        input_layout.addWidget(add_button)
        page_layout.addLayout(input_layout)

        note_table = QTableWidget(self)
        note_table.setColumnCount(2)
        note_table.setHorizontalHeaderLabels(["Title", "URL"])
        note_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        note_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        note_table.setEditTriggers(QTableWidget.NoEditTriggers) 
        note_table.setSelectionBehavior(QTableWidget.SelectRows)
        note_table.setSelectionMode(QTableWidget.SingleSelection)
        
        note_table.doubleClicked.connect(
            lambda index, col=collection_name, table=note_table: 
            self.open_selected_note(col, table)
        )
        page_layout.addWidget(note_table)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        open_button = QPushButton("OPEN SELECTED")
        open_button.clicked.connect(
            lambda checked, col=collection_name, table=note_table: 
            self.open_selected_note(col, table)
        )
        delete_button = QPushButton("DELETE SELECTED")
        delete_button.setObjectName("delete_button") # <-- SET OBJECT NAME HERE FOR CSS
        delete_button.clicked.connect(
            lambda checked, col=collection_name, table=note_table: 
            self.delete_selected_note(col, table)
        )
        action_layout.addStretch()
        action_layout.addWidget(open_button)
        action_layout.addWidget(delete_button)
        page_layout.addLayout(action_layout)

        self.collection_list_widget.addItem(collection_name)
        self.stacked_widget.addWidget(page_content_widget)
        
        self.collection_widgets[collection_name] = {
            "page_widget_ref": page_content_widget,
            "title_input": title_input,
            "url_input": url_input,
            "table": note_table
        }
        self.populate_collection_page(collection_name)

    def load_collections(self):
        """Loads all collections and notes from the JSON file."""
        if os.path.exists(COLLECTIONS_FILE):
            try:
                with open(COLLECTIONS_FILE, 'r', encoding='utf-8') as f:
                    self.collections_data = json.load(f)
            except json.JSONDecodeError:
                self.collections_data = {}
                QMessageBox.warning(self, "Error", f"Could not load notes from {COLLECTIONS_FILE}. Invalid JSON format.")
        else:
            self.collections_data = {}
            self.collections_data["General"] = []
            self.save_collections()

    def save_collections(self):
        """Save all collections and notes to a single JSON file."""
        with open(COLLECTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.collections_data, f, indent=4, ensure_ascii=False)

    def populate_all_collection_pages(self):
        """Populate all pages for all collections."""
        for collection_name in self.collections_data.keys():
            self.populate_collection_page(collection_name)

    def populate_collection_page(self, collection_name):
        """Populate the table for a specific collection."""
        if collection_name not in self.collection_widgets:
            return

        table = self.collection_widgets[collection_name]["table"]
        table.setRowCount(0)

        notes_for_collection = self.collections_data.get(collection_name, [])

        for row_idx, note_item in enumerate(notes_for_collection):
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QTableWidgetItem(note_item.get('title', 'No Title')))
            table.setItem(row_idx, 1, QTableWidgetItem(note_item.get('url', ''))) 

    def add_note_to_collection(self, collection_name, title_input_widget, url_input_widget):
        """Add a note to the specified collection."""
        title = title_input_widget.text().strip()
        url = url_input_widget.text().strip()

        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter a title for the note.")
            return

        new_note = {'title': title}
        if url:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url
            new_note['url'] = url

        self.collections_data.setdefault(collection_name, []).append(new_note)
        self.save_collections()
        self.populate_collection_page(collection_name)
        
        title_input_widget.clear()
        url_input_widget.clear()
        table = self.collection_widgets[collection_name]["table"]
        table.scrollToBottom()
        table.selectRow(len(self.collections_data[collection_name]) - 1)

    def delete_selected_note(self, collection_name, table_widget):
        """Delete the selected note from a specific collection's table."""
        selected_rows = table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Selection", "Please select a note to delete.")
            return

        row_index = selected_rows[0].row()
        
        note_to_delete = self.collections_data[collection_name][row_index]
        title_to_delete = note_to_delete.get('title', 'Unnamed Note')

        reply = QMessageBox.question(self, 'Delete Note',
                                     f"Are you sure you want to delete '{title_to_delete}' from '{collection_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            del self.collections_data[collection_name][row_index]
            self.save_collections()
            self.populate_collection_page(collection_name)
            
            if not self.collections_data[collection_name] and collection_name != "General":
                reply_delete_collection = QMessageBox.question(self, 'Delete Collection',
                                                             f"Collection '{collection_name}' is now empty. Do you want to remove this collection?",
                                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply_delete_collection == QMessageBox.Yes:
                    self.delete_collection(collection_name)


    def open_selected_note(self, collection_name, table_widget):
        """Open the URL of the selected note (if available)."""
        selected_rows = table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Selection", "Please select a note to open.")
            return

        row_index = selected_rows[0].row()
        url = self.collections_data[collection_name][row_index].get('url')
        if url:
            QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.information(self, "No URL", "Selected note does not have an associated URL.")

    def prompt_new_collection(self):
        """Open a dialog for the user to enter a new collection name."""
        self.show()
        self.raise_()
        self.activateWindow()

        collection_name, ok = QInputDialog.getText(self, "New Collection", "Enter new collection name:")
        if ok and collection_name:
            collection_name = collection_name.strip()
            if not collection_name:
                QMessageBox.warning(self, "Input Error", "Collection name cannot be empty.")
                return

            if collection_name in self.collections_data:
                QMessageBox.warning(self, "Collection Exists", f"Collection '{collection_name}' already exists.")
            else:
                self.collections_data[collection_name] = []
                self.save_collections()
                self._create_and_add_collection_page(collection_name)
                
                items = self.collection_list_widget.findItems(collection_name, Qt.MatchExactly)
                if items:
                    self.collection_list_widget.setCurrentItem(items[0])
                QMessageBox.information(self, "Collection Added", f"Collection '{collection_name}' has been added.")

    def delete_collection(self, collection_name):
        """Delete an entire collection."""
        if collection_name not in self.collections_data or collection_name == "General":
            QMessageBox.warning(self, "Action Denied", "The 'General' collection cannot be deleted.")
            return

        reply = QMessageBox.question(self, 'Delete Collection',
                                     f"Are you sure you want to delete the entire collection '{collection_name}' and all its notes?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            items = self.collection_list_widget.findItems(collection_name, Qt.MatchExactly)
            if items:
                row = self.collection_list_widget.row(items[0])
                self.collection_list_widget.takeItem(row)
                widget = self.stacked_widget.widget(row)
                if widget:
                    self.stacked_widget.removeWidget(widget)
                    widget.deleteLater()
            
            del self.collections_data[collection_name]
            del self.collection_widgets[collection_name]
            
            self.save_collections()
            QMessageBox.information(self, "Collection Deleted", f"Collection '{collection_name}' has been deleted.")
            
            if not self.collections_data:
                self.collections_data["General"] = []
                self.save_collections()
                self._create_and_add_collection_page("General")


    def prompt_add_note(self):
        """Bring window to front and focus input to add a note to the current collection."""
        self.show()
        self.raise_()
        self.activateWindow()
        
        current_item = self.collection_list_widget.currentItem()
        if current_item:
            current_collection_name = current_item.text()
            if current_collection_name in self.collection_widgets:
                self.collection_widgets[current_collection_name]["title_input"].setFocus()
        else:
            QMessageBox.warning(self, "No Active Collection", "Please select or create a collection first.")


    # --- Window Control Methods ---
    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.title_bar.update_max_restore_icon(self.isMaximized()) 

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(APP_ICON_PATH):
            self.tray_icon.setIcon(QIcon(APP_ICON_PATH))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon)) 
        
        self.tray_icon.setToolTip('OwMarker')

        tray_menu = QMenu()

        show_hide_action = QAction("Show/Hide Window", self)
        show_hide_action.triggered.connect(self.toggle_window_visibility)
        tray_menu.addAction(show_hide_action)

        add_note_action = QAction("Add Note (Current Collection)", self)
        add_note_action.triggered.connect(self.show_window_and_add_note_signal.emit)
        tray_menu.addAction(add_note_action)

        add_collection_action = QAction("Add New Collection", self)
        add_collection_action.triggered.connect(self.show_window_and_add_collection_signal.emit)
        tray_menu.addAction(add_collection_action)

        tray_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def toggle_window_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window_visibility()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
            self.tray_icon.showMessage(
                "OwMarker",
                "Application has been minimized to the system tray.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Tray Icon Error", "System tray not available.")
        sys.exit(1)

    app.setQuitOnLastWindowClosed(False)

    window = BookmarkManagerApp()
    window.show()
    sys.exit(app.exec_())