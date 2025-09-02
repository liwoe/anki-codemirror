# This file handels the hooks (names are self explaining as its a small file)

from aqt.editor import Editor

from . import utils
from .codemirror_dialog import CodeMirrorDialog

def on_insert_code_button_clicked(editor: Editor):
    if hasattr(editor, "codeMirrorDialog") and editor.codeMirrorDialog.isVisible():
        editor.codeMirrorDialog.raise_()
        editor.codeMirrorDialog.activateWindow()
        return

    js_save_selection = "if (window.selectionSaver) { window.selectionSaver.save(); }"
    editor.web.eval(js_save_selection)

    dialog = CodeMirrorDialog(editor.parentWindow, editor)
    editor.codeMirrorDialog = dialog
    editor.codeMirrorDialog.show()
    
def on_webview_message(handled: tuple[bool, object], message: str, context: object) -> tuple[bool, object]:
    if not isinstance(context, Editor):
        return handled

    if message.startswith("edit_code:"):
        editor = context
        _, block_id, encoded_raw = message.split(":", 2)
        
        dialog = CodeMirrorDialog(editor.parentWindow, editor, initial_code=encoded_raw, block_id=block_id)
        editor.codeMirrorDialog = dialog
        dialog.show()
        
        return (True, None)
        
    return handled

def add_editor_button(buttons: list, editor: Editor):
    icon_path = utils.USER_FILES_PATH / "icons" / "terminal.svg"
    btn = editor.addButton(
        icon=str(icon_path),
        cmd="insertLiveCodeBlock",
        func=lambda e=editor: on_insert_code_button_clicked(e),
        tip="Open CodeMirror Editor (Ctrl+Alt+C)",
        keys="Ctrl+Alt+C",
    )
    buttons.append(btn)
    return buttons
