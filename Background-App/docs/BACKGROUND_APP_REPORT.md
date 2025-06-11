# WorkMatrix Background Application Report

## 1. Introduction and Overall Purpose

The WorkMatrix Background Application is a desktop application designed to run silently in the background on a user's computer. Its primary purpose is to monitor user activity, collect various types of data related to work patterns, and synchronize this data with a central server (Supabase) and a local database. This data can then be used for productivity analysis, project management, and generating insights into work habits.

The application is intended to be cross-platform, with specific setup and service management scripts for Windows, macOS, and Linux.

Key functionalities include:
-   Tracking active application usage.
-   Monitoring user activity levels (keyboard/mouse input).
-   Capturing screenshots at configurable intervals.
-   (Potentially) Recording screen sessions.
-   Uploading collected data to a remote Supabase instance.
-   Storing data locally in an SQLite database as a buffer and for offline access.
-   Providing a WebSocket server for real-time communication with a frontend application.
-   Offering an HTTP API for certain control functions (e.g., starting/stopping monitoring).

## 2. Architecture Overview

The Background-App is a Python-based application structured into several key components:

*   **Main Application (`src/main.py`, `run.py`):** Initializes and orchestrates all other components. Handles startup, configuration loading, and service management.
*   **Monitoring Engine (`src/monitor.py`):** The core component responsible for managing data collectors and their schedules.
*   **Data Collectors (`src/collectors/`):** Modules responsible for gathering specific types of data:
    *   `activity_collector.py`: Tracks keyboard and mouse activity.
    *   `app_usage_collector.py`: Monitors the active application window and title.
    *   `screenshot_collector.py` / `screenshot_collector_new.py`: Captures screenshots of the user's screen.
    *   `recording_collector.py`: (Likely intended for screen recording, though implementation details need further review).
*   **Communication Services (`src/services/`):**
    *   `websocket_server.py`: Provides a WebSocket endpoint for real-time communication, primarily with the WorkMatrix frontend. Handles authentication and commands like start/stop monitoring.
    *   `http_server.py`: Offers a simple HTTP API for basic control.
    *   `monitor_api.py`: Appears to be an API layer for the monitor, possibly used by HTTP/WebSocket services.
*   **Data Management and Synchronization:**
    *   `src/utils/sqlite_manager.py` (and older `src/sqlite_manager.py`): Manages the local SQLite database for storing collected data.
    *   `src/utils/database.py`: Contains schema and database interaction logic.
    *   `src/services/supabase_service.py`: Handles interactions with the Supabase backend (authentication, data upload).
    *   `src/services/supabase_sync.py`: Manages the synchronization of local data to Supabase.
    *   `src/services/storage_manager.py` (and `src/utils/storage_manager.py` - potential duplication/versioning): Manages local file storage, especially for screenshots and recordings.
*   **Configuration (`src/config/`, `src/utils/config.py`):**
    *   `src/utils/config.py`: Centralized configuration management, likely loading from `.env` files and providing access to settings.
    *   `src/config/directory_config.py`: Manages application-specific directory paths.
    *   `src/config/screenshot_config.py` / `screenshot_config_new.py`: Configuration specific to screenshot capturing.
*   **Utilities (`src/utils/`):**
    *   `logging_config.py`: Sets up and configures logging for the application.
    *   `event_manager.py`: A system for managing and dispatching events within the application.
    *   `resource_manager.py`: Manages application resources.
    *   `init_supabase.py`: Initializes the Supabase client.
*   **Platform-Specific Services (`src/windows_service.py`, `src/macos_service.py`):** Scripts to run the application as a background service on Windows and macOS.
*   **Build and Setup Scripts (`build_background.py`, `build_exe.py`, `setup.py`, `setup_*.py/sh`):** Tools and scripts for packaging the application into an executable and setting it up on different operating systems.

## 3. Core Components and Functionality

### 3.1. Main Application (`src/main.py`, `run.py`)

*   `run.py`: Typically the entry point when running from source. It likely initializes the environment and calls `src/main.py`.
*   `src/main.py`:
    *   Initializes logging using `logging_config`.
    *   Loads application configuration using `src/utils/config.py`.
    *   Initializes the `EventManager`.
    *   Sets up the local SQLite database using `SQLiteManager` and `DatabaseUtil`.
    *   Initializes `SupabaseService` for communication with the backend.
    *   Starts the `WebSocketServer` and `HTTPServer`.
    *   Creates and starts the `Monitor` instance, which in turn starts the data collectors.
    *   Handles graceful shutdown of services.

### 3.2. Monitoring Engine (`src/monitor.py`)

*   The `Monitor` class is central to data collection.
*   It initializes and manages instances of the various data collectors (`ActivityCollector`, `AppUsageCollector`, `ScreenshotCollector`).
*   It uses a scheduling mechanism (e.g., `threading.Timer` or a similar approach) to run collectors at configured intervals.
*   It receives data from collectors and likely passes it to the `EventManager` or directly to data storage/sync components.
*   It can be started and stopped via commands (e.g., from WebSocket or HTTP API).

### 3.3. Data Collectors (`src/collectors/`)

#### 3.3.1. Activity Collector (`activity_collector.py`)
*   Monitors keyboard and mouse events to determine user activity levels.
*   Uses platform-specific libraries (e.g., `pynput`) to listen for input events.
*   Aggregates activity data over short intervals and reports metrics like "active", "idle".
*   The collected data is typically timestamped and includes user ID.

#### 3.3.2. Application Usage Collector (`app_usage_collector.py`)
*   Tracks the currently active application window and its title.
*   Uses platform-specific APIs to get information about the foreground window.
    *   On Windows, this might involve `pygetwindow` or `win32gui`.
    *   On macOS, AppleScript or other native interfaces.
    *   On Linux, `xlib` or similar X11 utilities.
*   Records the application name, window title, and timestamps. This helps in understanding how time is spent on different tasks and applications.

#### 3.3.3. Screenshot Collector (`screenshot_collector.py`, `screenshot_collector_new.py`)
*   Captures images of the user's screen(s) at regular, configurable intervals.
*   The `_new` version might indicate an updated or alternative implementation.
*   Uses libraries like `Pillow (PIL)` and `mss` for screen capture.
*   Screenshots are typically saved locally first (managed by `StorageManager`) and then queued for upload to Supabase.
*   Configuration options include capture frequency, image quality, and which monitor to capture (if multiple).
*   `src/config/screenshot_config.py` and `screenshot_config_new.py` likely hold settings for this collector.

#### 3.3.4. Recording Collector (`recording_collector.py`)
*   This module is intended for screen recording functionality.
*   The implementation details would involve capturing video frames (possibly with audio) and saving them as video files.
*   Libraries like `OpenCV` or platform-specific screen recording tools might be used.
*   Due to the data-intensive nature of recordings, careful management of storage and upload bandwidth is crucial.

### 3.4. Communication Services

#### 3.4.1. WebSocket Server (`src/services/websocket_server.py`)
*   Implements a WebSocket server (likely using libraries like `websockets`).
*   Listens on a configured port (e.g., `8765`).
*   **Purpose:** Enables real-time, two-way communication between the background app and a client (typically the WorkMatrix frontend).
*   **Authentication:**
    *   Requires an authentication message from the client upon connection.
    *   The auth message includes `user_id` and a `timestamp`.
    *   The server validates this, possibly against active user sessions or a token system.
*   **Functionality:**
    *   **Client Registration:** Manages connected clients.
    *   **Message Handling:** Processes incoming messages from clients.
        *   `auth`: For client authentication.
        *   `ping`: Client sends pings, server responds with `pong` to keep connection alive and check status.
        *   `start_monitoring`: Instructs the `Monitor` to begin data collection for the authenticated user.
        *   `stop_monitoring`: Instructs the `Monitor` to pause data collection.
    *   **Broadcasting/Sending Messages:** Can send status updates or data snippets back to the client.
    *   **Error Handling:** Manages connection errors and disconnections.
*   Refer to `docs/WEBSOCKET_INTEGRATION.md` for more details on the protocol.

#### 3.4.2. HTTP Server (`src/services/http_server.py`)
*   Implements a basic HTTP server (e.g., using Python's `http.server` or a lightweight framework like Flask/FastAPI if more complex).
*   **Purpose:** Provides a simple API for control and status checks, potentially for local administration or simpler integrations.
*   **Endpoints (example):**
    *   `/start`: To start monitoring.
    *   `/stop`: To stop monitoring.
    *   `/status`: To get the current status of the application.
*   The `src/services/monitor_api.py` might be used by this server to interact with the `Monitor`.

### 3.5. Data Management and Synchronization

#### 3.5.1. Local SQLite Database (`src/utils/sqlite_manager.py`, `src/utils/database.py`)
*   `src/utils/sqlite_manager.py`: Provides a wrapper for interacting with the SQLite database (`workmatrix.db` found in `scripts/` or a user-specific data directory).
    *   Handles database connection, cursor management, and query execution.
    *   Methods for creating tables, inserting data, querying data, and updating records.
*   `src/utils/database.py`: Defines the database schema (table structures, column names, data types) for data like activity logs, app usage, screenshots metadata, etc.
*   **Purpose:**
    *   Acts as a local buffer for collected data before it's synced to Supabase. This ensures data isn't lost if the internet connection is unavailable.
    *   Can store user preferences or application state locally.

#### 3.5.2. Supabase Integration (`src/services/supabase_service.py`, `src/services/supabase_sync.py`, `src/utils/init_supabase.py`)
*   `src/utils/init_supabase.py`: Initializes the Supabase client instance using credentials (URL and anon key) typically loaded from environment variables or the configuration file.
*   `src/services/supabase_service.py`:
    *   Contains functions to interact with Supabase backend.
    *   Handles user authentication with Supabase if needed by the background app itself (though frontend usually handles primary auth).
    *   Provides methods for uploading collected data (activity, app usage, screenshot files, etc.) to corresponding Supabase tables and storage buckets.
    *   Manages file uploads to Supabase Storage (e.g., for screenshots).
*   `src/services/supabase_sync.py`:
    *   Responsible for periodically checking the local SQLite database for new or unsynced data.
    *   Retrieves this data and uses `SupabaseService` to upload it to the Supabase backend.
    *   Manages sync status (e.g., marking records as synced in the local DB).
    *   Handles potential conflicts or errors during synchronization.

#### 3.5.3. Storage Management (`src/services/storage_manager.py`, `src/utils/storage_manager.py`)
*   There appear to be two `storage_manager.py` files. The one in `src/utils/` might be a more recent or refactored version.
*   **Purpose:** Manages the local file system storage for large data items like screenshots and screen recordings before they are uploaded or processed.
*   **Functionality:**
    *   Defines storage paths (e.g., for different data types or users).
    *   Handles saving files, deleting files, and checking storage limits.
    *   Works in conjunction with collectors (e.g., `ScreenshotCollector` saves files using this manager) and `SupabaseSync` (which would read files for upload).
    *   `src/config/directory_config.py` likely provides the base paths for storage.

### 3.6. Configuration Management (`.env`, `src/utils/config.py`, `src/config/`)

*   **`.env` file:** The primary way to store sensitive credentials (Supabase keys, API tokens) and environment-specific settings. This file is typically located in the `main application` directory or the root of the `Background-App` project during development. The `start_workmatrix.ps1` script explicitly checks for `.env` in `main application`.
*   **`src/utils/config.py`:**
    *   Loads configuration from the `.env` file (using libraries like `python-dotenv`).
    *   Provides a centralized `Config` class or object to access settings throughout the application.
    *   May define default values for settings if not found in `.env`.
*   **`src/config/` subdirectory:**
    *   `directory_config.py`: Defines and manages paths for logs, data storage, etc. Ensures consistent directory structures.
    *   `screenshot_config.py` / `screenshot_config_new.py`: Specific configuration parameters for the screenshot collector, such as capture interval, image format, quality, and storage paths. These might be loaded by the main `Config` object or used directly by the `ScreenshotCollector`.

### 3.7. Service Management (Windows, macOS, Linux)

The application is designed to run as a background service for persistence.

#### 3.7.1. Windows (`src/windows_service.py`, `setup_windows.py`)
*   `src/windows_service.py`: Implements the Windows service logic using libraries like `pywin32`.
    *   Defines the service class, handles service control manager (SCM) events (start, stop, pause, continue).
    *   Manages the service lifecycle.
*   `setup_windows.py`: A script likely used to install, uninstall, start, or stop the Windows service. It would interact with `windows_service.py` and the Windows SCM.

#### 3.7.2. macOS (`src/macos_service.py`, `setup_macos.sh`, `macos/com.workmatrix.service.plist`)
*   `src/macos_service.py`: Contains the core logic that the macOS service will run.
*   `macos/com.workmatrix.service.plist`: A LaunchAgent or LaunchDaemon property list file that defines how `launchd` (the macOS service manager) should run the application. It specifies the program to execute, run conditions, etc.
*   `setup_macos.sh`: A shell script to:
    *   Copy the `.plist` file to the appropriate LaunchAgents/LaunchDaemons directory (`~/Library/LaunchAgents` or `/Library/LaunchDaemons`).
    *   Load and start the service using `launchctl`.
    *   Handle uninstallation by unloading the service and removing the `.plist` file.

#### 3.7.3. Linux (`setup_linux.sh`, `linux/workmatrix.service`)
*   `linux/workmatrix.service`: A systemd service unit file.
    *   Defines how systemd (a common init system and service manager on Linux) should manage the WorkMatrix background process.
    *   Specifies the executable path, user to run as, restart policies, and dependencies.
*   `setup_linux.sh`: A shell script to:
    *   Copy the `workmatrix.service` file to the systemd directory (e.g., `/etc/systemd/system/`).
    *   Reload the systemd daemon (`systemctl daemon-reload`).
    *   Enable the service to start on boot (`systemctl enable workmatrix.service`).
    *   Start the service (`systemctl start workmatrix.service`).
    *   Handle uninstallation (stop, disable, remove service file).

### 3.8. Build and Deployment (`build_background.py`, `build_exe.py`, `setup.py`)

*   **`setup.py`:** A standard Python setup script using `setuptools`.
    *   Defines project metadata (name, version, author).
    *   Specifies dependencies (from `requirements.txt`).
    *   Can be used to build distributions (source, wheel) but is primarily used by PyInstaller in this context to gather package information.
*   **`build_background.py` / `build_exe.py`:** These are PyInstaller wrapper scripts.
    *   **Purpose:** To bundle the Python application, its dependencies, and assets into a single standalone executable for Windows, macOS, or Linux.
    *   **Functionality:**
        *   Use `PyInstaller` to analyze the Python scripts (`run.py` or `src/main.py` as entry point).
        *   Identify all required modules, libraries, and data files.
        *   Include hidden imports that PyInstaller might miss (this was a significant part of the earlier troubleshooting).
        *   Specify options like one-file vs. one-dir builds, console vs. windowed application, icon files, etc.
        *   The output is an executable (e.g., `workmatrix-background.exe` in the `main application` directory) and associated files if not a one-file build.
    *   `build_background.py` seems to be the more current and heavily modified script for building.

### 3.9. Logging (`src/utils/logging_config.py`)

*   `src/utils/logging_config.py`: Configures the Python `logging` module.
*   **Functionality:**
    *   Sets up log formatters (to define how log messages look).
    *   Sets up log handlers (e.g., `FileHandler` to write logs to a file, `StreamHandler` to output to console).
    *   Defines log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) for different handlers.
    *   Log files are typically stored in a `logs` directory, managed by `src/config/directory_config.py`.
    *   Provides a consistent way for all modules in the application to write log messages. This is crucial for debugging and monitoring the application's behavior.

### 3.10. Utilities (`src/utils/`)

*   **`event_manager.py`:**
    *   Implements a publish-subscribe event system.
    *   Allows different components of the application to communicate without being directly coupled.
    *   Example: A collector might publish a "new_data_collected" event, and a data sync module might subscribe to this event to process the data.
*   **`resource_manager.py`:**
    *   Likely handles loading and accessing application assets or resources, such as icons, configuration templates, or other data files that are part of the application bundle.
*   **`sync_manager.py`:**
    *   This might be an older or alternative version of `supabase_sync.py`, or it could manage other types of synchronization within the app. Its exact role needs to be clarified by examining its content more closely if it's actively used. Given the presence of `supabase_sync.py`, this might be deprecated or serve a different, specific purpose.

## 4. Data Flow Overview

1.  **Initialization:**
    *   Application starts (`run.py` -> `src/main.py`).
    *   Configuration is loaded.
    *   Logging, database, Supabase client, WebSocket/HTTP servers are initialized.
    *   The `Monitor` is started.
2.  **Data Collection (triggered by `Monitor`'s schedule):**
    *   `ActivityCollector` captures keyboard/mouse events.
    *   `AppUsageCollector` gets active window information.
    *   `ScreenshotCollector` takes screenshots.
    *   (If active) `RecordingCollector` captures screen video.
3.  **Local Storage:**
    *   Collected data (metadata, activity logs, app usage) is initially stored in the local SQLite database (`workmatrix.db`).
    *   Screenshots and recordings are saved to the local file system (managed by `StorageManager`). Paths/references might be stored in SQLite.
4.  **Real-time Communication (WebSocket):**
    *   Frontend connects to WebSocket server.
    *   Authenticates with `user_id`.
    *   Can send `start_monitoring` / `stop_monitoring` commands.
    *   Server can send status updates or (potentially) snippets of data back to the frontend.
5.  **Supabase Synchronization (`SupabaseSync`):**
    *   Periodically, `SupabaseSync` checks the local SQLite database for unsynced data.
    *   It retrieves this data and uses `SupabaseService` to:
        *   Upload tabular data (activity, app usage) to Supabase database tables.
        *   Upload files (screenshots, recordings) to Supabase Storage.
    *   Updates local records to mark them as synced.
6.  **API Interaction (HTTP):**
    *   External scripts or tools can interact with the HTTP API for basic control (start/stop/status).

## 5. Potential Areas of Duplication/Clarification

*   **Configuration Files:** `src/config.py` vs. `src/utils/config.py`. The latter seems to be the more comprehensive and actively used one.
*   **SQLite Management:** `src/sqlite_manager.py` vs. `src/utils/sqlite_manager.py`. Again, the version in `src/utils/` is likely the current one.
*   **Storage Management:** `src/services/storage_manager.py` vs. `src/utils/storage_manager.py`. Their specific roles and whether one supersedes the other should be verified. It's possible they manage different aspects of storage or one is an older version.
*   **Screenshot Collectors:** `screenshot_collector.py` vs. `screenshot_collector_new.py`. The `_new` suggests an updated version, and it should be confirmed which one is actively used by the `Monitor`.
*   **Sync Management:** `sync_manager.py` in `src/utils/` vs. `supabase_sync.py` in `src/services/`. `supabase_sync.py` is clearly for Supabase; the role of `sync_manager.py` needs to be understood if it's still in use.

## 6. Build and Deployment Process Summary

1.  **Dependencies:** Ensure Python and `pip` are installed. Install dependencies from `requirements.txt`.
2.  **Configuration:** Prepare the `.env` file with necessary Supabase credentials and other settings.
3.  **Build Executable:**
    *   Run `python build_background.py` (or `build_exe.py`).
    *   This uses PyInstaller to package the application into a distributable format (e.g., an `.exe` for Windows). The executable is typically placed in the `main application` directory.
4.  **Platform Setup:**
    *   **Windows:** Run `setup_windows.py` to install the application as a Windows service.
    *   **macOS:** Run `setup_macos.sh` to set up the LaunchAgent/LaunchDaemon.
    *   **Linux:** Run `setup_linux.sh` to set up the systemd service.
5.  **Running the Application:**
    *   Once set up as a service, the OS will manage starting the application on boot and keeping it running.
    *   For development/testing, `python run.py` can be used.
    *   The `start_workmatrix.ps1` script provides a unified way to start the background service and the frontend application for development or demonstration.

## 7. Conclusion

The WorkMatrix Background Application is a sophisticated tool for automated work activity tracking. It leverages a modular architecture with distinct components for data collection, local storage, cloud synchronization, and real-time communication. Its ability to run as a background service across multiple platforms, coupled with robust configuration and build processes, makes it a comprehensive solution for its intended purpose. Understanding the interaction between the collectors, the monitor, the local database, and the Supabase synchronization mechanism is key to comprehending its operation.
