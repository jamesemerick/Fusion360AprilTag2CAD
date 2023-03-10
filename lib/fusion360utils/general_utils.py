import pathlib
import sys
import time
import traceback
from typing import Optional

import adsk.core

app = adsk.core.Application.get()
ui = app.userInterface

# Attempt to read DEBUG flag from parent config.
try:
    from ... import config

    DEBUG = config.DEBUG
except:
    DEBUG = False


def log(
    message: str,
    level: adsk.core.LogLevels = adsk.core.LogLevels.InfoLogLevel,
    force_console: bool = False,
):
    """Utility function to easily handle logging in your app.

    Arguments:
    message -- The message to log.
    level -- The logging severity level.
    force_console -- Forces the message to be written to the Text Command window.
    """
    message = f"{time.ctime()}:: {message}"
    # Always print to console, only seen through IDE.
    print(message)

    # Log all errors to Fusion log file.
    if level == adsk.core.LogLevels.ErrorLogLevel:
        log_type = adsk.core.LogTypes.FileLogType
        app.log(message, level, log_type)

    # If config.DEBUG is True write all log messages to the console.
    if DEBUG or force_console:
        log_type = adsk.core.LogTypes.ConsoleLogType
        app.log(message, level, log_type)


def handle_error(name: str, show_message_box: bool = False):
    """Utility function to simplify error handling.

    Arguments:
    name -- A name used to label the error.
    show_message_box -- Indicates if the error should be shown in the message box.
                        If False, it will only be shown in the Text Command window
                        and logged to the log file.
    """

    log("===== Error =====", adsk.core.LogLevels.ErrorLogLevel)
    log(f"{name}\n{traceback.format_exc()}", adsk.core.LogLevels.ErrorLogLevel)

    # If desired you could show an error as a message box.
    if show_message_box:
        ui.messageBox(f"{name}\n{traceback.format_exc()}")


def get_project_dir() -> pathlib.Path:
    ui = adsk.core.Application.get().userInterface

    folder_dialog = ui.createFolderDialog()
    folder_dialog.title = "Choose ARAAS Project Folder"
    dialog_result = folder_dialog.showDialog()

    if dialog_result == adsk.core.DialogResults.DialogOK:
        return pathlib.Path(folder_dialog.folder)
    raise RuntimeError("A ARAAS project directory must be specified.")


def get_file(msg: str, file_filer: str = "*.*") -> pathlib.Path:
    """Prompts to select a file."""

    ui = adsk.core.Application.get().userInterface
    file_dialog = ui.createFileDialog()
    file_dialog.isMultiSelectEnabled = False
    file_dialog.filter = file_filer
    file_dialog.title = msg

    result = file_dialog.showOpen()

    if result == adsk.core.DialogResults.DialogOK:
        return pathlib.Path(file_dialog.filename)
    else:
        ui.messageBox("A file must be selected.")
        sys.exit()


def get_download_dir(app: adsk.core.Application) -> Optional[pathlib.Path]:
    ui = app.userInterface
    folder_dialog = ui.createFolderDialog()
    folder_dialog.title = "Choose a local download directory."
    dialog_result = folder_dialog.showDialog()
    if dialog_result == adsk.core.DialogResults.DialogOK:
        return pathlib.Path(folder_dialog.folder)
    else:
        ui.messageBox("A download directory must be selected.")
        sys.exit()
