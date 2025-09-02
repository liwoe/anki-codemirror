<h1>Anki CodeMirror Editor</h1>
<p>A powerful, integrated code editor for Anki that brings beautiful syntax highlighting and a rich editing experience directly into your flashcards.</p>

<h2>Overview</h2>
<p>This add-on replaces the default text areas for code with a full-featured CodeMirror instance. It's designed for students, developers, and anyone who wants to create flashcards with clean, readable, and beautifully formatted code snippets.</p>

<h2>Features</h2>
<ul>
<li><strong>Rich Syntax Highlighting:</strong> Supports a wide variety of languages out of the the box, including Python, JavaScript, HTML, CSS, SQL, C++, and more.</li>
<li><strong>Theme Support:</strong> Easily switch between popular code editor themes to match your preference.</li>
<li><strong>Live In-Editor Preview:</strong> See your formatted code directly within the Anki editor.</li>
<li><strong>Seamless Editing:</strong> Double-click any code block in the editor to open it for modifications.</li>
<li><strong>Easy Configuration:</strong> A simple configuration dialog lets you choose which note types should use the CodeMirror editor and select your global theme.</li>
<li><strong>Highly Customizable:</strong> Advanced users can directly edit the CSS files to fine-tune the appearance of the code blocks.</li>
</ul>

<h2>Installation</h2>
<ol>
<li>Download the <code>.ankiaddon</code> file from the releases page.</li>
<li>Open Anki and go to <code>Tools &gt; Add-ons</code>.</li>
<li>Drag and drop the downloaded <code>.ankiaddon</code> file into the Add-ons window.</li>
<li>Restart Anki to complete the installation.</li>
</ol>

<h2>How to Use</h2>
<h3>Adding a New Code Block</h3>
<ol>
<li>Open the Anki editor for any note type you've enabled in the configuration.</li>
<li>Click the <strong><code>&lt;/&gt;</code></strong> button in the editor toolbar.</li>
<li>A dialog will appear with the CodeMirror editor. Select your language, write your code, and click <strong>"Insert Code"</strong>.</li>
<li>The formatted code block will be added to your card.</li>
</ol>

<h3>Editing an Existing Code Block</h3>
<ol>
<li>In the Anki editor, simply <strong>double-click</strong> on any code block that was created with this add-on.</li>
<li>The CodeMirror editor dialog will open with the existing code, ready for you to edit.</li>
<li>Click <strong>"Update Code"</strong> to save your changes.</li>
</ol>

<h2>Configuration</h2>
<p>You can configure the add-on by going to the Anki Tools section and clicking CodeMirror Configuration</p>
<p>In the configuration window, you can:</p>
<ul>
<li><strong>Select Note Types:</strong> Check the box next to any note type you want the CodeMirror editor to be active on.</li>
<li><strong>Choose a Theme:</strong> Select your preferred editor theme from the dropdown menu. This theme will be used in both the editor dialog and the rendered cards.</li>
<li><strong>Customize Styles:</strong> Click the <strong>"Open Custom Styles Folder"</strong> button to directly open the folder containing the CSS files. You can edit these files to change fonts, colors, padding, and more.</li>
</ul>

<h2>Advanced Customization</h2>
<p>For more direct control over the appearance, you can edit the add-on's style files. You can access these by going to the Anki Add-ons dialog, selecting "Anki CodeMirror Editor", and clicking the <strong>"Config"</strong> button. This will open the custom styles folder in your system's file explorer.</p>
<p>Inside this folder, you can edit the CSS files to change properties like <code>font-size</code>, <code>font-family</code>, padding, and the editor's colors to perfectly match your preferences.</p>

<h2>License</h2>
<p>This project is licensed under the <strong>Creative Commons Attribution-NonCommercial 4.0 International License</strong>. You are free to share and adapt the material, but you may not use it for commercial purposes. See the <a href="LICENSE">LICENSE</a> file for more details.</p>

<h2>Contributing & Credits</h2>
<p>This add-on is built upon the fantastic <a href="https://codemirror.net/">CodeMirror</a> library.</p>
<p>Contributions are welcome! Please see the <a href="CONTRIBUTORS.md">CONTRIBUTORS.md</a> file for more information on how to contribute to the project.</p>
