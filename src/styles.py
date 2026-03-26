MODERN_STYLE = """
/* Màu nền chính */
QMainWindow, #main_content, #sidebar { background-color: #202020; border: none; }

/* Sidebar */
QListWidget { background-color: transparent; border: none; color: #e0e0e0; font-size: 14px; outline: none; }
QListWidget::item { padding: 10px; border-radius: 5px; margin: 2px 10px; border: none; }
QListWidget::item:hover { background-color: #333333; } /* Hover màu xám */
QListWidget::item:selected { background-color: #444444; color: #ffffff; font-weight: bold; border: none; }

/* Buttons */
QPushButton { background-color: transparent; color: #e0e0e0; border: none; border-radius: 6px; padding: 8px 15px; font-weight: bold; }
QPushButton:hover { background-color: #333333; } /* Hover nút màu xám */
#btn_add { background-color: transparent; color: #e0e0e0; border: none; }
#btn_add:hover { background-color: #333333; }

/* Add Collection (+) */
#btn_add_collection { background-color: transparent; color: #e0e0e0; border-radius: 4px; font-size: 16px; padding: 4px 8px; border: none; }
#btn_add_collection:hover { background-color: #333333; }

/* Widget Note */
#note_widget { background-color: transparent; border-radius: 8px; margin: 5px; border: none; }
#note_widget:hover { background-color: #333333; border: none; }

/* Scroll Area & Input */
QScrollArea, QWidget#scroll_content { background-color: transparent; border: none; }
QLineEdit, QTextEdit { background-color: transparent; border: none; color: #e0e0e0; border-radius: 5px; padding: 5px; }
QLineEdit:focus, QTextEdit:focus { background-color: #333333; border: none; }

/* (MessageBox / InputDialog) */
QMessageBox, QInputDialog { background-color: #202020; color: white; border: none; }
QMessageBox QLabel, QInputDialog QLabel { color: white; border: none; }
"""