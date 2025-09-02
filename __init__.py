from aqt import gui_hooks, mw
from aqt.qt import QAction

# --- Import your addon's components ---
from .hooks import add_editor_button, on_webview_message
from .save_handler import on_editor_will_save_note
from . import field_check_manager
from . import config
from . import config_actions
from .config_dialog import show_config_dialog

# --- Load the configuration on startup ---
config.load_config()

# --- Register all the hooks for the add-on ---
# Adds the CodeMirror button to the editor
gui_hooks.editor_did_init_buttons.append(add_editor_button)

# Handles double-click events to edit a code block
gui_hooks.webview_did_receive_js_message.append(on_webview_message)

# Cleans the HTML before a note is saved
gui_hooks.add_cards_will_add_note.append(on_editor_will_save_note)

# --- Apply the field check bypass patch (so cloze cards can be added) ---
field_check_manager.apply_field_check_patch()

mw.addonManager.setConfigAction(__name__, config_actions.open_styles_folder)
# --- Add the unified configuration menu item ---
action_config = QAction("CodeMirror Configuration...", mw)
action_config.triggered.connect(show_config_dialog)
mw.form.menuTools.addAction(action_config)

# Expose the user_files folder to the web view
mw.addonManager.setWebExports(__name__, r"user_files/.*")