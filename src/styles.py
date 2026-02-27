MODERN_STYLE = """
/* Màu nền chính */
QMainWindow, #main_content { background-color: #1e1e2e; }

/* Sidebar */
#sidebar { background-color: #181825; border-right: 1px solid #313244; }
QListWidget { background-color: transparent; border: none; color: #cdd6f4; font-size: 14px; outline: none; }
QListWidget::item { padding: 10px; border-radius: 5px; margin: 2px 10px; }
QListWidget::item:hover { background-color: #313244; }
QListWidget::item:selected { background-color: #89b4fa; color: #11111b; font-weight: bold; }

/* Nút bấm Menu & Add */
QPushButton { background-color: #313244; color: #cdd6f4; border: none; border-radius: 6px; padding: 8px 15px; font-weight: bold; }
QPushButton:hover { background-color: #45475a; }
#btn_add { background-color: #a6e3a1; color: #11111b; }
#btn_add:hover { background-color: #94e2d5; }

/* Widget Note */
#note_widget { background-color: #313244; border-radius: 8px; margin: 5px; }
#note_widget:hover { background-color: #45475a; border: 1px solid #89b4fa; }

/* Scroll Area */
QScrollArea { border: none; background-color: transparent; }
QWidget#scroll_content { background-color: transparent; }

/* Input Dialog */
QLineEdit, QTextEdit { background-color: #181825; border: 1px solid #45475a; color: #cdd6f4; border-radius: 5px; padding: 5px; }
"""