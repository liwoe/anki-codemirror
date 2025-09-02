// We sync this file to anki media so mobile can use this too
// Also: we inject this into the card

(function () {
    function initializeCodeMirrorBlocks() {
        // Find all the simple spans that are our placeholders for code blocks.
        const codeSpans = document.querySelectorAll('.codemirror-anki[data-language]');

        if (codeSpans.length === 0 || typeof CodeMirror === 'undefined') {
            return;
        }

        const globalTheme = window.CODE_MIRROR_GLOBAL_THEME || 'dracula';

        codeSpans.forEach(span => {
            // This element will be replaced, so we don't need to check if it's
            // already rendered. The querySelector won't find it again next time.

            const code = span.textContent;
            const language = span.dataset.language;

            // Create a new container for the full CodeMirror instance.
            // A <div> is more suitable than <pre> for this.
            const container = document.createElement('div');

            // IMPORTANT: Replace the original span with our new container *before*
            // initializing CodeMirror. CodeMirror needs the element to be in the DOM.
            span.parentNode.replaceChild(container, span);

            // Now, initialize a full CodeMirror instance on the container.
            CodeMirror(container, {
                value: code,              // The code to display
                mode: language,           // The language for syntax highlighting
                theme: globalTheme,       // The theme from your addon's config
                lineNumbers: true,        // Numbers for code
                readOnly: 'nocursor',     // Makes it non-editable and hides the blinking cursor
                lineWrapping: true,       // Optional: wrap long lines
            });
        });
    }

    // Run the function once the card is fully loaded.
    if (document.readyState === "complete") {
        initializeCodeMirrorBlocks();
    } else {
        window.addEventListener("load", initializeCodeMirrorBlocks);
    }

    // Use a MutationObserver to handle content changes in modern Anki versions.
    if (window.MutationObserver) {
        const observer = new MutationObserver((mutations) => {
            if (mutations.some(m => m.addedNodes.length > 0)) {
                initializeCodeMirrorBlocks();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
})();