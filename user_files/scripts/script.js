// This script creates the codemirror editor where you can type.

document.addEventListener("DOMContentLoaded", function () {
    
    // =================================================================
    // SECTION 1: Get references to all HTML elements
    // =================================================================
    const insertButton = document.getElementById("insert-button");
    const clozeButton = document.getElementById("cloze-button");
    const clozeSameButton = document.getElementById("cloze-same-button");
    const langSelector = document.getElementById("language-selector");

    // =================================================================
    // SECTION 2: Load configuration passed from Python
    // =================================================================
    const config = window.CM_CONFIG || {};
    const initialLanguage = config.language || "python";
    const activeTheme = config.activeTheme || "dracula";

    if (config.buttonText) {
        insertButton.textContent = config.buttonText;
    }
    
    // Set the language dropdown to its last used value
    langSelector.value = initialLanguage;

    // =================================================================
    // SECTION 3: Define all helper functions
    // =================================================================

    function isColorLight(color) {
        if (!color) return false;
        const [r, g, b] = color.match(/\d+/g).map(Number);
        // Using the luminance formula
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b);
        return luminance > 128;
    }

    // This function reads the editor's colors and applies them to the UI
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
            
            // A matching bracket is a great source for a theme's main accent color
            const accentElement = document.querySelector('.CodeMirror-matchingbracket');
            const accentColor = accentElement ? window.getComputedStyle(accentElement).color : gutterFgColor;
            
            bodyStyles.setProperty('--editor-bg', bgColor);
            bodyStyles.setProperty('--editor-fg', fgColor);
            bodyStyles.setProperty('--ui-bg', uiBgColor);
            bodyStyles.setProperty('--ui-border', gutterFgColor);
            bodyStyles.setProperty('--ui-hover-bg', gutterFgColor);
            bodyStyles.setProperty('--gutter-fg', gutterFgColor);
            bodyStyles.setProperty('--accent-color', accentColor);
            
            // NEW: Smartly set the insert button's text color for readability
            if (insertButton) {
                if (isColorLight(accentColor)) {
                    // If the button background is light, use a dark text color.
                    insertButton.style.color = "#333333";
                } else {
                    // If the button background is dark, use a bright text color.
                    insertButton.style.color = "#ff9800"; // A nice, visible orange
                }
            }
        }, 50);
    }

    // This function adds cloze deletions
    function addCloze(increment) {
        const editor = window.editor;
        if (!editor) return;
        const fullText = editor.getValue();
        let maxCloze = 0;
        const clozeRegex = /{{\s*c(\d+)::/g;
        let match;
        while ((match = clozeRegex.exec(fullText)) !== null) {
            const num = parseInt(match[1], 10);
            if (num > maxCloze) { maxCloze = num; }
        }
        let clozeNum = increment ? maxCloze + 1 : (maxCloze === 0 ? 1 : maxCloze);
        const selectedText = editor.getSelection();
        const clozeString = `{{c${clozeNum}::${selectedText || ''}}}`;
        editor.replaceSelection(clozeString);
        if (!selectedText) {
            const cursorPos = editor.getCursor();
            editor.setCursor({ line: cursorPos.line, ch: cursorPos.ch - 2 });
        }
        editor.focus();
    }

    // This function prepares and sends the final code to Anki
    function submitCode() {
        const codeElement = document.querySelector(".CodeMirror-code");
        if (!codeElement) { return; }

        const currentLanguage = window.editor.getOption("mode");
        const rawCode = editor.getValue();
        const highlightedHtml = codeElement.innerHTML;
        const encodedRawCode = btoa(unescape(encodeURIComponent(rawCode)));
        const encodedHtml = btoa(unescape(encodeURIComponent(highlightedHtml)));

        sendToPython(`insert_code:${currentLanguage}:${encodedRawCode}:${encodedHtml}`);
    }

    // This function handles communication back to Python
    function sendToPython(command) {
        if (window.pybridge && window.pybridge.send) {
            pybridge.send(command);
        } else if (window.pycmd) {
            pycmd(command);
        } else {
            console.error("No Anki communication bridge found.");
        }
    }

    // =================================================================
    // SECTION 4: Initialize the editor and set up all event listeners
    // (This is the part you were asking about)
    // =================================================================

    // Initialize the CodeMirror editor itself
    window.editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
        lineNumbers: true,
        mode: initialLanguage,
        theme: activeTheme,
        autoCloseBrackets: true,
        matchBrackets: true,
        lineWrapping: true,
        extraKeys: {
            "Ctrl-Enter": (cm) => submitCode()
        }
    });

    // Set focus to the editor so you can start typing right away
    editor.focus();
    
    // Sync the UI colors for the first time on load
    syncUiToTheme();

    // Listen for changes on the language dropdown
    langSelector.addEventListener("change", function () {
        const newLang = this.value;
        window.editor.setOption("mode", newLang);
        sendToPython(`set_lang:${newLang}`);
        window.editor.focus();
    });

    
    // Listen for clicks on the buttons
    insertButton.addEventListener("click", submitCode);
    clozeButton.addEventListener("click", () => addCloze(true));
    clozeSameButton.addEventListener("click", () => addCloze(false));
    
    // Listen for keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        if (window.editor && window.editor.hasFocus()) {
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

    // Listen for window resizing to prevent visual glitches
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.editor) {
                window.editor.refresh();
            }
        }, 150);
    });
});
