import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QMenu, QDialog, 
                               QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor, QAction

class NoteDialog(QDialog):
    def __init__(self, parent=None, note_text="", link=""):
        super().__init__(parent)
        self.setWindowTitle("Note Details")
        self.setFixedSize(350, 170)
        self.setStyleSheet("""
            QDialog {
                background-color: #202020;
                border: none;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #333333;
                border: none;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton {
                background-color: #202020;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        
        self.note_input = QLineEdit(note_text)
        self.note_input.setPlaceholderText("Enter note content...")
        self.link_input = QLineEdit(link)
        self.link_input.setPlaceholderText("https://...")

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)

        layout = QFormLayout(self)
        layout.addRow("Content:", self.note_input)
        layout.addRow("Link:", self.link_input)
        layout.addRow("", btn_save)
        layout.setSpacing(10)

    def get_data(self):
        return self.note_input.text().strip(), self.link_input.text().strip()

class NoteWidget(QFrame):
    deleted = Signal(object) 
    edited = Signal(object, str, str) 

    def __init__(self, note_text, link):
        super().__init__()
        self.setObjectName("note_widget")
        self.note_text = note_text
        self.link = link
        self.init_ui()

    def init_ui(self):
        display_text = ""
        if self.note_text and self.link: display_text = f"{self.note_text}"
        elif self.note_text: display_text = f"{self.note_text}"
        elif self.link: display_text = f"{self.link}"
        else: display_text = "Empty Note"

        self.lbl = QLabel(display_text)
        self.lbl.setWordWrap(True)
        self.lbl.setStyleSheet("color: #e0e0e0; font-size: 14px; padding: 10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lbl)

        if self.link:
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.link:
            webbrowser.open(self.link)

    def contextMenuEvent(self, event):
        # Right-click menu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #252525; color: #e0e0e0; border: none; border-radius: 5px; padding: 4px; } QMenu::item { padding: 6px 20px; border-radius: 4px; } QMenu::item:selected { background-color: #444444; color: white; }")
        
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)
        
        menu.addAction(edit_action)
        menu.addAction(delete_action)

        action = menu.exec(self.mapToGlobal(event.pos()))
        
        if action == edit_action:
            dialog = NoteDialog(self, self.note_text, self.link)
            if dialog.exec():
                new_note, new_link = dialog.get_data()
                self.edited.emit(self, new_note, new_link)
        elif action == delete_action:
            self.deleted.emit(self)