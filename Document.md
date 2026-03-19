# Technical Documentation: Modern Bookmark App

This document provides a comprehensive technical overview of the **Modern Bookmark App**, detailing its system architecture, workflow, and a granular breakdown of its modules, classes, and functions. This guide is intended for developers and maintainers looking to understand the core mechanics of the application.

---

## 1. System Architecture

The application is built using **Python** and **PySide6** (Qt for Python). It follows a highly modular, event-driven architecture designed for local desktop environments. The architecture is broadly categorized into four layers:

1. **Presentation Layer (UI):** Managed by PySide6 widgets (`app_window.py`, `components.py`). Responsible for rendering the layout, handling user inputs, and displaying data.
2. **Core Logic Layer:** Handles the business logic, window lifecycle, and application state (`app_window.py`).
3. **Background Services Layer:** Manages global OS-level event hooks and system tray integration (`hotkey_manager.py`, `tray_manager.py`).
4. **Data Persistence Layer:** Manages I/O operations, ensuring data and settings are safely serialized and deserialized into local JSON files (`data_manager.py`, `settings_manager.py`).

---

## 2. Inter-Process Communication & Data Flow

The application relies heavily on the **Qt Signals and Slots** mechanism to facilitate communication between different modules, especially when crossing thread boundaries.

* **Signals:** Events emitted by an object when its state changes (e.g., a button is `clicked`, or a global hotkey is detected).
* **Slots:** Callable functions designed to react to a specific Signal.

**Cross-Thread Safety:** The `keyboard` module listens for hotkeys on a separate background thread. To safely update the UI or access the system clipboard, `HotkeyWorker` emits a custom signal (`execute_copy`) that is caught by a Slot running safely on the Main UI Thread.

---

## 3. Module and Class Breakdown

Below is a detailed breakdown of every file, class, and critical function in the system.

### `main.py`
The entry point of the application.
* Instantiates the `QApplication`.
* Sets `app.setQuitOnLastWindowClosed(False)` to ensure the background process stays alive when the main window is closed.
* Initializes and displays the `MainWindow`.
* Starts the main Event Loop (`app.exec()`).

### `src/app_window.py`
Contains the `MainWindow` class, which serves as the central hub of the application.

**Initialization & UI**
* `__init__()`: Initializes the `DataManager`, `SettingsManager`, UI components, `TrayManager`, and `HotkeyWorker`.
* `init_ui()`: Constructs the user interface utilizing `QSplitter`, `QFrame`, `QVBoxLayout`, and `QHBoxLayout`. Defines the sidebar and main content layout.
* `toggle_menu()`: Controls the `QPropertyAnimation` to smoothly expand or collapse the sidebar.
* `on_menu_animation_finished()`: Callback that resets the `maximumWidth` of the sidebar after the animation to allow the user to freely resize it via the `QSplitter`.

**Event Handling**
* `closeEvent(event)`: Overrides the default window close behavior. Rejects the close event (`event.ignore()`) and hides the window to the system tray unless a graceful exit is explicitly triggered by the tray menu.

**Collection Management (CRUD)**
* `load_collections()`: Clears and repopulates the sidebar `QListWidget` with collection keys.
* `on_collection_selected(item)`: Updates the current context, adds the collection to recent settings, and calls `render_notes()`.
* `add_collection()`: Prompts the user via `QInputDialog` to create a new key in the database dictionary.
* `show_collection_context_menu(pos)`: Generates a contextual `QMenu` providing actions to Rename, Delete, or Set a Hotkey.
* `rename_collection(item)`: Validates and updates a collection key. Safely transfers configuration data in `settings_manager` to match the new key.
* `delete_collection(item)`: Deletes the key from the dictionary, removes associated configurations from settings, and cascades changes to the UI.
* `set_collection_hotkey(item)`: Prompts for a shortcut string and registers it via the `SettingsManager`.

**Note Management (CRUD)**
* `render_notes()`: Iterates over the selected collection's array, dynamically instantiating and appending `NoteWidget` objects to the scroll area.
* `add_note()`, `delete_note(widget)`, `edit_note(widget, new_note, new_link)`: Standard CRUD operations that manipulate the data dictionary in RAM and subsequently call `save_current_state()`.
* `add_note_from_hotkey(collection_name, selected_text)`: Receives data intercepted by the background hook. Uses simple string matching to determine if the payload is a URL or standard text, then pushes it to the database.

### `src/components.py`
Contains custom PySide6 UI widgets.

**`NoteDialog` (Inherits `QDialog`)**
* A simple form layout presenting two `QLineEdit` fields for users to input or edit a note and its associated hyperlink.
* `get_data()`: Returns the sanitized tuple of `(note_text, link_text)`.

**`NoteWidget` (Inherits `QFrame`)**
* Represents an individual note item in the UI. 
* Defines custom signals: `deleted(object)` and `edited(object, str, str)`.
* `init_ui()`: Evaluates the presence of text vs. link to determine which icon (`📄`, `📝`, or `🔗`) to display. Sets cursor to `PointingHandCursor` if a link exists.
* `mousePressEvent(event)`: Overridden to detect left-clicks. Launches the system's default web browser targeting the stored URL via the `webbrowser` module.
* `contextMenuEvent(event)`: Overridden to instantiate an edit/delete context menu on right-click. Emits the corresponding signal based on user selection.

### `src/data_manager.py`
Handles I/O operations for the core database.

**`DataManager`**
* `load_data()`: Attempts to open and parse `bookmarks.json`. If missing or corrupt, it creates a dictionary containing onboarding instructions (default data).
* `save_data(data)`: Serializes the Python dictionary into UTF-8 JSON. Uses `indent=4` for human readability and `ensure_ascii=False` for unicode character support.

### `src/settings_manager.py`
Handles I/O operations for application configurations.

**`SettingsManager`**
* `load_settings()`, `save_settings()`: Reads/writes `settings.json` which tracks `recent_collections` and `hotkeys`.
* `add_recent_collection(collection_name)`: Implements a basic Least Recently Used (LRU) algorithm. It unshifts the requested collection to the beginning of the list and truncates the list to a maximum length of 3.
* `set_hotkey(collection_name, hotkey)`: Assigns or unassigns a specific string identifier to a collection key.
* `remove_collection_data(collection_name)`: Cleanup utility that scrubs a collection from recent history and hotkey configurations if the collection is deleted globally.

### `src/tray_manager.py`
Provides System Tray functionality.

**`TrayManager` (Inherits `QSystemTrayIcon`)**
* `build_menu()`: A dynamic factory function executed immediately before the tray menu appears. It polls the `SettingsManager` to generate quick-add actions for the user's top 3 collections.
* `on_tray_activated(reason)`: Toggles the visibility of the `MainWindow` when the user double-clicks the tray icon.
* `add_note_to_collection(collection_name)`: Instantiates a `NoteDialog` directly from the system tray context, bypassing the main UI entirely to insert a record into the database.
* `quit_app()`: Sets a strict `is_quitting` flag that commands `MainWindow.closeEvent` to bypass the interception routine, allowing `QApplication.quit()` to safely terminate the process.

### `src/hotkey_manager.py`
Provides low-level keyboard hooking for OS-wide functionality.

**`HotkeyWorker` (Inherits `QObject`)**
* `setup_hotkeys()`: Unhooks existing keyboard listeners via `keyboard.unhook_all()`, fetches configurations from `SettingsManager`, and registers listeners asynchronously using `keyboard.add_hotkey`. Sets `suppress=False` to preserve native keyboard behaviors.
* `on_hotkey(collection_name)`: The callback triggered by the `keyboard` library. Because this executes on a background thread, it cannot safely interact with Qt GUI components. It emits the `execute_copy` signal.
* `perform_copy(collection_name)`: The connected slot that executes on the main thread. It caches the current clipboard state, uses `keyboard.send('ctrl+c')` to programmatically copy selected text, and delays further execution by 150ms via `QTimer.singleShot` to ensure the OS clipboard buffer has flushed.
* `check_clipboard(collection_name, old_text)`: Reads the updated clipboard payload. If valid content is detected, it emits the `hotkey_triggered(collection_name, text)` signal, passing the data up to the `MainWindow` for insertion.