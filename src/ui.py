from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSystemTrayIcon, QMenu, QAction, QMessageBox,
    QLabel, QSizePolicy, QTabWidget, QStyle, QInputDialog
)
from PyQt5.QtGui import QIcon, QDesktopServices, QMouseEvent
from PyQt5.QtCore import QUrl, Qt, QPoint, pyqtSignal
import sys
import json
import os

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
    