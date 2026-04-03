import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QMenu, QDialog, 
                               QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QFrame, QApplication)
from PySide6.QtCore import Qt, Signal, QTimer
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
        self.is_editing = False
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.execute_single_click)
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Display Mode ---
        self.display_widget = QWidget()
        self.display_layout = QVBoxLayout(self.display_widget)
        self.display_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl = QLabel()
        self.lbl.setWordWrap(True)
        self.lbl.setStyleSheet("color: #e0e0e0; font-size: 14px; padding: 10px;")
        self.display_layout.addWidget(self.lbl)

        # --- Edit Mode ---
        self.edit_widget = QWidget()
        self.edit_layout = QVBoxLayout(self.edit_widget)
        self.edit_layout.setContentsMargins(10, 10, 10, 10)
        self.edit_layout.setSpacing(5)

        edit_style = "QLineEdit { background-color: #333333; border: none; color: #e0e0e0; border-radius: 5px; padding: 6px; }"
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Enter note content...")
        self.note_edit.setStyleSheet(edit_style)
        
        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("https://...")
        self.link_edit.setStyleSheet(edit_style)

        btn_layout = QHBoxLayout()
        btn_style = "QPushButton { background-color: #333333; color: white; border: none; border-radius: 4px; padding: 4px 12px; } QPushButton:hover { background-color: #444444; }"
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet(btn_style)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet(btn_style)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        self.btn_save.clicked.connect(self.save_inline)
        self.btn_cancel.clicked.connect(self.cancel_inline)

        self.edit_layout.addWidget(self.note_edit)
        self.edit_layout.addWidget(self.link_edit)
        self.edit_layout.addLayout(btn_layout)

        self.edit_widget.hide()

        self.main_layout.addWidget(self.display_widget)
        self.main_layout.addWidget(self.edit_widget)

        self.update_display()

    def update_display(self):
        display_text = ""
        if self.note_text and self.link: display_text = f"{self.note_text}"
        elif self.note_text: display_text = f"{self.note_text}"
        elif self.link: display_text = f"{self.link}"
        else: display_text = "Empty Note"

        self.lbl.setText(display_text)

        if self.link:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.link and not self.is_editing:
            self.click_timer.start(250)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_timer.stop()
            self.start_edit()

    def execute_single_click(self):
        if self.link and not self.is_editing:
            webbrowser.open(self.link)

    def start_edit(self):
        self.is_editing = True
        self.display_widget.hide()
        self.note_edit.setText(self.note_text)
        self.link_edit.setText(self.link)
        self.edit_widget.show()
        self.note_edit.setFocus()
        self.setCursor(Qt.ArrowCursor)

    def save_inline(self):
        new_note = self.note_edit.text().strip()
        new_link = self.link_edit.text().strip()
        
        self.is_editing = False
        self.edit_widget.hide()
        self.display_widget.show()
        
        if new_note != self.note_text or new_link != self.link:
            self.edited.emit(self, new_note, new_link)
            
        self.update_display()

    def cancel_inline(self):
        self.is_editing = False
        self.edit_widget.hide()
        self.display_widget.show()
        self.update_display()

    def contextMenuEvent(self, event):
        # Right-click menu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #252525; color: #e0e0e0; border: none; border-radius: 5px; padding: 4px; } QMenu::item { padding: 6px 20px; border-radius: 4px; } QMenu::item:selected { background-color: #444444; color: white; }")
        
        copy_action = QAction("Copy", self)
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)
        
        menu.addAction(copy_action)
        menu.addAction(edit_action)
        menu.addAction(delete_action)

        action = menu.exec(self.mapToGlobal(event.pos()))
        
        if action == copy_action:
            QApplication.clipboard().setText(self.note_text if self.note_text else self.link)
        elif action == edit_action:
            self.start_edit()
        elif action == delete_action:
            self.deleted.emit(self)