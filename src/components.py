import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QMenu, QDialog, 
                               QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QFrame, QApplication, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QCursor, QAction

class NoteDialog(QDialog):
    def __init__(self, parent=None, name="", description="", links=None):
        super().__init__(parent)
        self.setWindowTitle("Note Details")
        self.setFixedSize(420, 320)
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
            QTextEdit {
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

        if links is None:
            links = []

        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Enter note name...")

        self.description_input = QTextEdit(description)
        self.description_input.setPlaceholderText("Enter note description...")
        self.description_input.setFixedHeight(80)

        self.links_input = QTextEdit("\n".join(links))
        self.links_input.setPlaceholderText("One link per line (https://...)")
        self.links_input.setFixedHeight(100)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)

        layout = QFormLayout(self)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Links:", self.links_input)
        layout.addRow("", btn_save)
        layout.setSpacing(10)

    def get_data(self):
        links = [line.strip() for line in self.links_input.toPlainText().splitlines() if line.strip()]
        return (
            self.name_input.text().strip(),
            self.description_input.toPlainText().strip(),
            links
        )

class NoteWidget(QFrame):
    deleted = Signal(object) 
    edited = Signal(object, str, str, list) 

    def __init__(self, note_name, note_description, links):
        super().__init__()
        self.setObjectName("note_widget")
        self.note_name = note_name
        self.note_description = note_description
        self.links = links if isinstance(links, list) else []
        self.is_editing = False
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.execute_single_click)
        self.index_in_db: int | None = None
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

        line_edit_style = "QLineEdit { background-color: #333333; border: none; color: #e0e0e0; border-radius: 5px; padding: 6px; }"
        text_edit_style = "QTextEdit { background-color: #333333; border: none; color: #e0e0e0; border-radius: 5px; padding: 6px; }"

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter note name...")
        self.name_edit.setStyleSheet(line_edit_style)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter note description...")
        self.description_edit.setStyleSheet(text_edit_style)
        self.description_edit.setFixedHeight(70)

        self.links_edit = QTextEdit()
        self.links_edit.setPlaceholderText("One link per line")
        self.links_edit.setStyleSheet(text_edit_style)
        self.links_edit.setFixedHeight(80)

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

        self.edit_layout.addWidget(self.name_edit)
        self.edit_layout.addWidget(self.description_edit)
        self.edit_layout.addWidget(self.links_edit)
        self.edit_layout.addLayout(btn_layout)

        self.edit_widget.hide()

        self.main_layout.addWidget(self.display_widget)
        self.main_layout.addWidget(self.edit_widget)

        self.update_display()

    def update_display(self):
        if self.note_name:
            display_text = self.note_name
        elif self.note_description:
            display_text = self.note_description
        elif self.links:
            display_text = self.links[0]
        else:
            display_text = "Empty Note"

        if self.note_description and self.note_description != display_text:
            display_text += f"\n{self.note_description}"

        if self.links:
            display_text += f"\n({len(self.links)} link{'s' if len(self.links) != 1 else ''})"

        self.lbl.setText(display_text)

        if self.links:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.links and not self.is_editing:
            self.click_timer.start(250)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_timer.stop()
            self.start_edit()
        super().mouseDoubleClickEvent(event)

    def execute_single_click(self):
        if self.links and not self.is_editing:
            webbrowser.open(self.links[0])

    def start_edit(self):
        self.is_editing = True
        self.display_widget.hide()
        self.name_edit.setText(self.note_name)
        self.description_edit.setText(self.note_description)
        self.links_edit.setText("\n".join(self.links))
        self.edit_widget.show()
        self.name_edit.setFocus()
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def save_inline(self):
        new_name = self.name_edit.text().strip()
        new_description = self.description_edit.toPlainText().strip()
        new_links = [line.strip() for line in self.links_edit.toPlainText().splitlines() if line.strip()]

        self.is_editing = False
        self.edit_widget.hide()
        self.display_widget.show()

        if (
            new_name != self.note_name
            or new_description != self.note_description
            or new_links != self.links
        ):
            self.edited.emit(self, new_name, new_description, new_links)

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
            lines = []
            if self.note_name:
                lines.append(self.note_name)
            if self.note_description:
                lines.append(self.note_description)
            if self.links:
                lines.extend(self.links)
            QApplication.clipboard().setText("\n".join(lines))
        elif action == edit_action:
            self.start_edit()
        elif action == delete_action:
            self.deleted.emit(self)