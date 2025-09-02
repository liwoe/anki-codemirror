# This file contains actions related to the add-on's configuration,
# such as opening relevant folders for user customization.

import os
from aqt import mw
from aqt.utils import openFolder

# Import the utility functions to get the correct user files path.
from . import utils

def open_styles_folder():
    """
    Opens the 'user_files/styles' directory in the system's default file explorer.
    
    This provides a convenient way for users to directly access and edit the
    CSS files that control the appearance of the CodeMirror editor.
    """
    # Construct the full, absolute path to the styles directory.
    styles_path = os.path.join(utils.USER_FILES_PATH, "styles")
    
    # Check if the directory actually exists before trying to open it.
    if os.path.isdir(styles_path):
        # Use Anki's built-in, cross-platform function to open a folder.
        openFolder(styles_path)
    else:
        # Log an error if the folder is missing for some reason.
        print(f"CodeMirror Add-on: Styles folder not found at {styles_path}")

