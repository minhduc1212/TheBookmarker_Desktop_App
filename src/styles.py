MODERN_STYLE = """
/* Main background color */
QMainWindow, #main_content, #sidebar { background-color: #202020; border: none; }

/* ScrollBar Styling (Modern, no arrows) */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: transparent;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:vertical:pressed {
    background: #555555;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: transparent;
    min-width: 30px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover, QScrollBar::handle:horizontal:pressed {
    background: #555555;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    background: none;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* Sidebar */
QListWidget { background-color: transparent; border: none; color: #e0e0e0; font-size: 14px; outline: none; }
QListWidget::item { padding: 10px; border-radius: 5px; margin: 2px 10px; border: none; }
QListWidget::item:hover { background-color: #333333; } /* Gray hover */
QListWidget::item:selected { background-color: #444444; color: #ffffff; font-weight: bold; border: none; }

/* Buttons */
QPushButton { background-color: transparent; color: #e0e0e0; border: none; border-radius: 6px; padding: 8px 15px; font-weight: bold; }
QPushButton:hover { background-color: #333333; } /* Gray button hover */
#btn_add { background-color: transparent; color: #e0e0e0; border: none; font-size: 28px; padding: 2px 15px; }
#btn_add:hover { background-color: #333333; }

/* Add Collection (+) */
#btn_add_collection { background-color: transparent; color: #e0e0e0; border-radius: 4px; font-size: 16px; padding: 4px 8px; border: none; }
#btn_add_collection:hover { background-color: #333333; }

/* Note Widget */
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