// This script initializes the CodeMirror editor inside the Anki dialog,
// sets up its configuration, and handles communication back to the main Anki window.

document.addEventListener("DOMContentLoaded", () => {
    // --- CONFIGURATION ---
    const config = window.CM_CONFIG || {};
    const buttonText = config.buttonText || "Insert Code";
    const initialLanguage = config.language || "python";
    const activeTheme = config.activeTheme || "dracula";
    const starterCode = config.starterCode || {};

    // --- ELEMENT SETUP ---
    const insertButton = document.getElementById("insert-button");
    const langSelect = document.getElementById("language-select");
    const clozeButton = document.getElementById("cloze-button");
    const clozeSameButton = document.getElementById("cloze-same-button");
    const starterCodeButton = document.getElementById("starter-code-button");

    if (insertButton) {
        insertButton.textContent = buttonText;
    }
    if (langSelect) {
        langSelect.value = initialLanguage;
    }
    
    // =================================================================
    // SECTION: Helper Functions
    // =================================================================

    /**
     * Checks if a given RGB color is light or dark.
     * @param {string} color - The RGB color string (e.g., "rgb(40, 42, 54)").
     * @returns {boolean} - True if the color is light, false otherwise.
     */
    function isColorLight(color) {
        if (!color) return false;
        const [r, g, b] = color.match(/\d+/g).map(Number);
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b);
        return luminance > 128;
    }

    /**
     * Reads the computed styles from the CodeMirror theme and applies them
     * to the surrounding UI elements for a cohesive look.
     */
    function syncUiToTheme() {
        setTimeout(() => {
            const cmElement = document.querySelector('.CodeMirror');
            if (!cmElement) return;

            const styles = window.getComputedStyle(cmElement);
            const bodyStyles = document.body.style;
            const bgColor = styles.backgroundColor;
            const fgColor = styles.color;
            const activeLine = document.querySelector('.CodeMirror-activeline-background');
            const uiBgColor = activeLine ? window.getComputedStyle(activeLine).backgroundColor : bgColor;
            const gutterText = document.querySelector('.CodeMirror-linenumber');
            const gutterFgColor = gutterText ? window.getComputedStyle(gutterText).color : fgColor;
            const accentElement = document.querySelector('.CodeMirror-matchingbracket');
            const accentColor = accentElement ? window.getComputedStyle(accentElement).color : gutterFgColor;
            
            bodyStyles.setProperty('--editor-bg', bgColor);
            bodyStyles.setProperty('--editor-fg', fgColor);
            bodyStyles.setProperty('--ui-bg', uiBgColor);
            bodyStyles.setProperty('--ui-border', gutterFgColor);
            bodyStyles.setProperty('--ui-hover-bg', gutterFgColor);
            bodyStyles.setProperty('--gutter-fg', gutterFgColor);
            bodyStyles.setProperty('--accent-color', accentColor);
            
            if (insertButton && isColorLight(accentColor)) {
                insertButton.style.color = "#333333";
            }
        }, 50);
    }

    /**
     * Wraps the selected text with Anki's cloze syntax.
     * @param {boolean} increment - If true, creates a new cloze number (c2, c3...). 
     * If false, uses the last-used cloze number.
     */
    function addCloze(increment) {
        const editor = window.editor;
        if (!editor) return;
        let maxCloze = 0;
        const clozeRegex = /{{\s*c(\d+)::/g;
        let match;
        while ((match = clozeRegex.exec(editor.getValue())) !== null) {
            maxCloze = Math.max(maxCloze, parseInt(match[1], 10));
        }
        const clozeNum = increment ? maxCloze + 1 : (maxCloze || 1);
        const selectedText = editor.getSelection();
        const clozeString = `{{c${clozeNum}::${selectedText || ''}}}`;
        editor.replaceSelection(clozeString);
        if (!selectedText) {
            const cursorPos = editor.getCursor();
            editor.setCursor({ line: cursorPos.line, ch: cursorPos.ch - 2 });
        }
        editor.focus();
    }
    
    /** Inserts pre-defined starter code for the current language into the editor. */
    function insertStarterCode() {
        const editor = window.editor;
        if (!editor) return;
        const currentLanguage = editor.getOption("mode");
        const snippet = starterCode[currentLanguage];
        if (snippet) {
            editor.setValue(snippet);
        }
        editor.focus();
    }

    /**
     * Encodes the editor's content and sends it back to Python.
     */
    function submitCode() {
        const codeElement = document.querySelector(".CodeMirror-code");
        if (!codeElement) {
            console.error("Could not find the '.CodeMirror-code' element to get highlighted HTML.");
            return;
        }

        const rawCode = window.editor.getValue();
        const highlightedHtml = codeElement.innerHTML;
        
        const encodedRaw = btoa(unescape(encodeURIComponent(rawCode)));
        const encodedHtml = btoa(unescape(encodeURIComponent(highlightedHtml)));
        const currentLang = window.editor.getOption("mode");
        
        sendToPython(`insert_code:${currentLang}:${encodedRaw}:${encodedHtml}`);
    }

    /**
     * Robustly sends a command to Anki's Python backend.
     * @param {string} command - The command string to send.
     */
    function sendToPython(command) {
        if (window.pybridge && window.pybridge.send) {
            pybridge.send(command);
        } else if (window.pycmd) {
            pycmd(command);
        } else {
            console.error("No Anki communication bridge found.");
        }
    }

    /**
     * Injects CSS into the document head to style the Vim command bar.
     */
    function injectVimDialogStyles() {
        const styleId = 'cm-vim-dialog-styles';
        if (document.getElementById(styleId)) return;

        const style = document.createElement('style');
        style.id = styleId;
        style.innerHTML = `
            .CodeMirror-dialog {
                background-color: var(--ui-bg, #282a36);
                color: var(--editor-fg, #f8f8f2);
                border-top: 1px solid var(--ui-border, #6272a4);
                padding: 0.4em 0.8em;
            }

            .CodeMirror-dialog input {
                border: none;
                outline: none;
                background: transparent;
                width: 20em;
                color: inherit;
                font-family: monospace;
            }
        `;
        document.head.appendChild(style);
    }

    // =================================================================
    // SECTION: Editor Initialization and Event Listeners
    // =================================================================

    const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
        lineNumbers: true,
        mode: initialLanguage,
        theme: activeTheme,
        keyMap: "vim",
        autoCloseBrackets: true,
        matchBrackets: true,
        lineWrapping: true,
        styleActiveLine: true,
        extraKeys: {
            "Ctrl-Enter": (cm) => submitCode(),
            "Ctrl-B": () => insertStarterCode()
        }
    });
    window.editor = editor;

    editor.on('keydown', function(cm, event) {
        if (event.key === 'Escape') {
            event.stopPropagation();
        }
    });

    // --- Attach Event Listeners ---
    if (insertButton) insertButton.addEventListener("click", submitCode);
    if (clozeButton) clozeButton.addEventListener("click", () => addCloze(true));
    if (clozeSameButton) clozeSameButton.addEventListener("click", () => addCloze(false));
    if (starterCodeButton) starterCodeButton.addEventListener("click", insertStarterCode);
    
    if (langSelect) {
        langSelect.addEventListener("change", (e) => {
            const newLang = e.target.value;
            editor.setOption("mode", newLang);
            sendToPython(`set_lang:${newLang}`);
            editor.focus();
        });
    }

    document.addEventListener('keydown', (event) => {
        if (editor.hasFocus()) {
            if (event.ctrlKey && event.shiftKey && !event.altKey && event.key.toLowerCase() === 'c') {
                event.preventDefault();
                addCloze(true);
            }
            if (event.ctrlKey && event.shiftKey && event.altKey && event.key.toLowerCase() === 'c') {
                event.preventDefault();
                addCloze(false);
            }
        }
    });

    // --- Final Setup ---
    setTimeout(() => {
        editor.focus();
        editor.refresh();
        // Programmatically enter Insert Mode after the editor is ready.
        // This ensures the user can start typing immediately.
        if (editor.state.vim && editor.state.vim.insertMode === false) {
            CodeMirror.Vim.handleKey(editor, 'i');
        }
    }, 100);
    
    syncUiToTheme();
    injectVimDialogStyles();
});

