# Modern Bookmark App

A sleek, modern desktop application built with Python and PySide6 for managing your bookmarks, links, and quick notes. 

## Features

* **Collection Management**: Organize your links and notes into customizable collections.
* **Modern UI**: Dark-themed, responsive interface with smooth animations and an adjustable sidebar (Splitter).
* **System Tray & Background Execution**: Minimizes to the system tray instead of closing. You can add notes directly to your top 3 recent collections right from the tray context menu.
* **Global Hotkeys**: Highlight text anywhere on your PC (browser, document, etc.) and hit a custom hotkey to automatically copy and save it to a specific collection.
* **Local Storage**: Data and settings are safely stored locally in JSON format (`bookmarks.json` and `settings.json`).

## Requirements

* Python 3.x
* PySide6
* keyboard (for global hotkey support)

## Installation

1. Clone or download the project files.
2. Open your terminal or command prompt in the project directory.
3. Install the required dependencies:

   ```bash
   pip install PySide6 keyboard
   ```

## Usage

Run the main application:
```bash
python main.py
```

* **Adding a Hotkey**: Right-click any collection in the sidebar and select "Cài đặt phím tắt...". For example, enter `ctrl+shift+a`.
* **Quick Save**: Highlight text, press your custom hotkey, and a tray notification will confirm the text was saved!
* **Background Mode**: Closing the main window (using the `X` button) will minimize the app to the system tray. Right-click the tray icon and select "Thoát" to quit completely.