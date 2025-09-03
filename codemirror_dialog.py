# This script defines the main graphical interface for the CodeMirror editor add-on.
# It creates a pop-up dialog (a QDialog) that hosts a web view. This web view,
# in turn, loads the CodeMirror editor, allowing users to write and edit code
# before inserting it into an Anki note field.

import base64
import json
from bs4 import BeautifulSoup
import time

from aqt import mw
from aqt.editor import Editor
from aqt.webview import AnkiWebView
from aqt.qt import QDialog, QVBoxLayout

from . import config
from . import utils
from . import starter_code  # NEW: Import the starter code snippets

class CodeMirrorWebView(AnkiWebView):
    """
    A custom AnkiWebView subclass to correctly handle local asset paths.
    
    Anki's default webview loader doesn't know how to find files inside the
    add-on's own folder. This class overrides the methods for loading JS and CSS
    to prepend the correct local web path, allowing CodeMirror's files to be loaded.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def bundledScript(self, fname: str) -> str:
        # If the script is part of our add-on, build a path to it.
        if "codemirror/" in fname or "scripts/" in fname:
            return f'<script src="{utils.WEB_PATH}/{fname}"></script>'
        # Otherwise, fall back to Anki's default script loading.
        return super().bundledScript(fname)

    def bundledCSS(self, fname: str) -> str:
        # If the stylesheet is part of our add-on, build a path to it.
        if "codemirror/" in fname or "styles/" in fname:
            return f'<link rel="stylesheet" type="text/css" href="{utils.WEB_PATH}/{fname}">'
        # Otherwise, fall back to Anki's default CSS loading.
        return super().bundledCSS(fname)

class CodeMirrorDialog(QDialog):
    """
    The main dialog window for the CodeMirror editor.
    
    This class sets up the window, loads the webview with the editor,
    and handles communication between the Python backend and the JavaScript frontend.
    """
    def __init__(self, parent, editor: Editor, initial_code: str = "", block_id: str = None):
        """
        Initializes the dialog.
        
        Args:
            parent: The parent widget, usually the main Anki window.
            editor: An instance of Anki's editor, used to insert the final code.
            initial_code: Base64 encoded code to load if editing an existing block.
            block_id: The unique ID of the code block if editing.
        """
        super().__init__(parent)
        self.editor = editor
        self.initial_code = initial_code
        self.block_id = block_id

        # --- Basic Window Setup ---
        self.setWindowTitle("Code Editor")
        self.resize(900, 700)
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # --- Webview and Bridge Setup ---
        # The webview hosts the HTML/JS of the editor.
        self.web = CodeMirrorWebView(self)
        # The bridge command sets up a communication channel from JS back to Python.
        # When pycmd() is called in JS, it triggers the _on_bridge_cmd method here.
        self.web.set_bridge_command(self._on_bridge_cmd, self)

        # --- Configuration Loading ---
        # Load user preferences, like the theme and last-used language.
        self.active_theme = config.CONFIG.get(config.CONFIG_KEY_GLOBAL_THEME, 'dracula')
        last_lang = mw.col.conf.get("anki_codemirror_last_lang", "python")
        button_text = "Update Code" if self.block_id else "Insert Code"

        # Read the CSS content for the selected theme. This is needed later for
        # styling the code block *inside* the Anki editor field.
        self.active_theme_css = ""
        theme_path = utils.USER_FILES_PATH / "codemirror" / "theme" / f"{self.active_theme}.css"
        if theme_path.exists():
            self.active_theme_css = theme_path.read_text(encoding="utf-8")

        # --- Asset Loading for the Dialog ---
        # Define all CSS and JS files needed for the editor dialog itself.
        css_files = [
            "codemirror/lib/codemirror.css",
            f"codemirror/theme/{self.active_theme}.css",
            "styles/styles.css"
        ]
        
        js_files = [
            "codemirror/lib/codemirror.js", "codemirror/addon/edit/closebrackets.js",
            "codemirror/addon/edit/matchbrackets.js", "codemirror/mode/clike/clike.js",
            "codemirror/mode/python/python.js", "codemirror/mode/javascript/javascript.js",
            "codemirror/mode/ruby/ruby.js", "codemirror/mode/sql/sql.js", "codemirror/mode/css/css.js",
            "codemirror/mode/xml/xml.js", "codemirror/mode/htmlmixed/htmlmixed.js", "scripts/script.js"
        ]
        
        # --- HTML and Initial Data Injection ---
        # Load the base HTML file for the dialog.
        html_file = utils.USER_FILES_PATH / "codemirror_index.html"
        html_content = html_file.read_text(encoding="utf-8")
        
        # Use BeautifulSoup to parse the HTML and inject the initial code
        # into the textarea if we are in editing mode.
        soup = BeautifulSoup(html_content, "html.parser")
        textarea = soup.find("textarea", {"id": "code-editor"})
        if textarea and self.initial_code:
            try:
                decoded_initial_code = base64.b64decode(self.initial_code).decode("utf-8")
                textarea.string = decoded_initial_code
            except Exception:
                textarea.string = "Error decoding code."

        body_content = soup.body.decode_contents() if soup.body else ""

        # Create a JavaScript configuration object to pass Python variables
        # to the frontend. This is how the JS knows the theme, language, etc.
        init_script = f"""<script>
            window.CM_CONFIG = {{
                buttonText: {json.dumps(button_text)},
                language: {json.dumps(last_lang)},
                activeTheme: {json.dumps(self.active_theme)},
                starterCode: {json.dumps(starter_code.STARTER_CODE)}
            }};
        </script>""" # MODIFIED: Added starterCode to the config object

        # Finally, load the prepared HTML, CSS, and JS into the webview.
        self.web.stdHtml(body=body_content, css=css_files, js=js_files, context=self, head=init_script)
        self.layout().addWidget(self.web)


    def _on_bridge_cmd(self, cmd: str):
        """
        Handles commands sent from the JavaScript frontend via pycmd().
        """
        # Command to save the user's last selected language.
        if cmd.startswith("set_lang:"):
            _, lang = cmd.split(":", 1)
            mw.col.conf["anki_codemirror_last_lang"] = lang
            return

        # Main command to insert or update the code block in the Anki editor.
        if cmd.startswith("insert_code:"):
            # The JS sends the language, raw code, and syntax-highlighted HTML.
            _, lang, encoded_raw, encoded_html = cmd.split(":", 3)
            decoded_html = base64.b64decode(encoded_html).decode("utf-8")
            
            # Read the base CSS files needed to style the final code block.
            cm_base_css = (utils.USER_FILES_PATH / "codemirror/lib/codemirror.css").read_text(encoding="utf-8")
            
            # Combine all necessary CSS to be injected into the Anki editor field.
            css_to_inject = f"""
                {cm_base_css}
                {self.active_theme_css}
                .anki-code-block {{
                    display: inline-block;
                    vertical-align: middle;
                    height: auto;
                    border-radius: 6px;
                    padding: 4px 8px;
                    padding-left: 2em;
                    font-family: 'Fira Code', monospace;
                    font-size: 16px;
                    max-width: 100%;
                    overflow-x: auto;
                    text-align: left;
                }}
            """
            
            self.editor.web.setFocus()

            # --- Logic for Updating vs. Inserting ---
            if self.block_id:
                # --- UPDATE EXISTING BLOCK ---
                # If a block_id exists, we are in editing mode.
                # This JS will find the existing block by its ID and update its content.
                js_injector = f"""
                (() => {{
                    const shadowRoot = document.activeElement?.shadowRoot;
                    if (!shadowRoot) return;
                    const block = shadowRoot.getElementById('{self.block_id}');
                    if (block) {{
                        block.dataset.rawCode = {json.dumps(encoded_raw)};
                        block.dataset.language = {json.dumps(lang)};
                        block.querySelector('.CodeMirror-code').innerHTML = {json.dumps(decoded_html)};
                    }}
                }})();
                """
            else:
                # --- INSERT NEW BLOCK ---
                # If no block_id, we are inserting a new code block.
                unique_id = f"code-block-{time.time_ns()}"
                theme_class = f"cm-s-{self.active_theme}"
                
                # Construct the HTML for the new code block.
                # contenteditable="false" prevents direct editing in the Anki field.
                # data-* attributes store the raw code and language for later editing.
                html_to_insert = f"""
                <span id="{unique_id}" 
                      class="anki-code-block CodeMirror {theme_class}" 
                      contenteditable="false" 
                      data-raw-code="{encoded_raw}"
                      data-language="{lang}">
                    <div class="CodeMirror-code">{decoded_html}</div>
                </span><br>
                """
                
                # This complex JS blob is injected into the Anki editor's webview.
                js_injector = f"""
                (() => {{
                    setTimeout(() => {{
                        if (window.selectionSaver) {{ window.selectionSaver.restore(); }}
                        document.execCommand('insertHTML', false, {json.dumps(html_to_insert)});
                        const shadowRoot = document.activeElement?.shadowRoot;
                        if (!shadowRoot) return;
                        
                        // Attach a double-click listener to the editor field, but only once.
                        if (!window.ankiCodeBlockListenerAttached) {{
                            shadowRoot.addEventListener('dblclick', (event) => {{
                                const codeBlock = event.target.closest('.anki-code-block');
                                if (codeBlock) {{
                                    // If a code block is double-clicked, send a command back
                                    // to Python to open the editor dialog again.
                                    pycmd(`edit_code:${{codeBlock.id}}:${{codeBlock.dataset.rawCode}}`);
                                }}
                            }});
                            window.ankiCodeBlockListenerAttached = true;
                        }}

                        // Inject or update the CSS styles for all code blocks in the field.
                        const styleId = 'codemirror-syntax-styles';
                        let style = shadowRoot.getElementById(styleId);
                        if (!style) {{
                            style = document.createElement('style');
                            style.id = styleId;
                            shadowRoot.appendChild(style);
                        }}
                        style.innerHTML = {json.dumps(css_to_inject)};
                    }}, 50);
                }})();
                """
            
            # Execute the prepared JavaScript in the Anki editor's webview.
            self.editor.web.eval(js_injector)
            # Close the dialog successfully.
            self.accept()