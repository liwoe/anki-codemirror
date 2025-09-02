# This script manages the add-on's assets (CSS and JavaScript files).
# Its primary responsibilities are:
# 1. Defining which assets the add-on requires.
# 2. Syncing these assets from the add-on's installation folder to Anki's media folder. So mobile can render code as well
# 3. Generating the necessary HTML to include these assets in Anki card templates.

from pathlib import Path

from aqt import mw
from . import utils

# --- Asset Definition ---
# Lists of CSS and JS files required by the add-on. These paths are relative
# to the add-on's root directory (USER_FILES_PATH).

CSS_FILES = [
    "codemirror/lib/codemirror.css",
    "styles/reviewer_style.css",
]

JS_FILES = [
    "codemirror/lib/codemirror.js",
    "codemirror/addon/runmode/runmode.js",
    "codemirror/mode/meta.js",
    "codemirror/mode/python/python.js",
    "codemirror/mode/javascript/javascript.js",
    "codemirror/mode/clike/clike.js",
    "codemirror/mode/ruby/ruby.js",
    "codemirror/mode/sql/sql.js",
    "codemirror/mode/css/css.js",
    "codemirror/mode/xml/xml.js",
    "codemirror/mode/htmlmixed/htmlmixed.js",
    "scripts/reviewer_script.js",
]

# A unique prefix for all assets copied to the media folder.
# This is crucial to prevent filename conflicts with other add-ons or user media.
PREFIX = "_codemirror_anki_"


def get_prefixed_filename(path: Path) -> str:
    """
    Constructs the final filename for an asset to be stored in the media folder.
    Example: 'python.js' -> '_codemirror_anki_python.js'
    """
    return f"{PREFIX}{path.name}"


def _sync_file(source_path: Path, media_dir: Path):
    """
    Core logic for syncing a single asset file to Anki's media folder.

    This function implements a "delete-then-write" strategy to ensure assets are
    always up-to-date and to work around Anki's media hashing behavior. Anki
    may create files with a hash in the name (e.g., 'style-abc123.css') if it
    detects content changes. To prevent accumulation of old, hashed files, this
    function proactively removes all variants of the target file before writing
    the new version.
    """
    if not source_path.exists():
        return

    prefixed_name = get_prefixed_filename(source_path)
    base_name = Path(prefixed_name).stem
    extension = Path(prefixed_name).suffix

    # Create a glob pattern to find all existing versions of the asset.
    # e.g., for '_codemirror_anki_reviewer_style.css', the pattern is
    # '_codemirror_anki_reviewer_style*.css' to match hashed versions.
    glob_pattern = f"{base_name}*{extension}"
    
    # Use standard Pathlib to glob for files on the filesystem, which is more
    # stable across different Anki versions than relying on internal media DB methods.
    files_on_disk = media_dir.glob(glob_pattern)
    filenames_to_remove = [p.name for p in files_on_disk]

    # If any old versions are found, use Anki's API to remove them.
    # This ensures they are properly removed from the media database as well.
    if filenames_to_remove:
        mw.col.media.trash_files(filenames_to_remove)

    # Read the new file's content and write it using Anki's media API.
    # mw.col.media.write_data handles adding the file to the media database
    # and marking it for synchronization with AnkiWeb.
    data = source_path.read_bytes()
    mw.col.media.write_data(prefixed_name, data)


def sync_assets_to_media_folder():
    """
    Iterates through all defined CSS and JS assets and syncs them
    to the media folder using the _sync_file helper.
    """
    media_dir = Path(mw.col.media.dir())
    addon_dir = utils.USER_FILES_PATH
    files_to_sync = CSS_FILES + JS_FILES

    for relative_path_str in files_to_sync:
        source_path = addon_dir / relative_path_str
        _sync_file(source_path, media_dir)


def sync_theme_to_media_folder(theme_name: str):
    """
    Syncs a single, dynamically chosen CodeMirror theme file to the media folder.
    """
    media_dir = Path(mw.col.media.dir())
    theme_path = utils.USER_FILES_PATH / "codemirror" / "theme" / f"{theme_name}.css"
    _sync_file(theme_path, media_dir)


def get_mobile_resources_html(theme_name: str) -> str:
    """
    Generates an HTML block containing <link> and <script> tags for all assets.

    This block is intended to be injected into Anki card templates. It ensures that
    the necessary CSS and JS are loaded during card review.
    """
    # Trigger a sync every time this is called. This ensures that if the user
    # changes a file or theme, the changes are immediately reflected in the
    # media folder without needing an Anki restart.
    sync_assets_to_media_folder()
    sync_theme_to_media_folder(theme_name)
    
    # Build the <link> tags for the CSS files.
    css_links = ""
    for file in CSS_FILES:
        filename = get_prefixed_filename(Path(file))
        css_links += f'<link rel="stylesheet" type="text/css" href="{filename}">'
    
    # Add the link for the currently selected theme.
    theme_filename = get_prefixed_filename(Path(f"{theme_name}.css"))
    css_links += f'<link rel="stylesheet" type="text/css" href="{theme_filename}">'

    # Build the <script> tags for the JavaScript files.
    js_links = ""
    for file in JS_FILES:
        filename = get_prefixed_filename(Path(file))
        js_links += f'<script src="{filename}"></script>'

    # Assemble the final HTML block. It's wrapped in a hidden div.
    # A global JS variable is also created to pass the theme name to the scripts.
    return f"""
    <div id="{PREFIX}resources" style="display: none;">
        {css_links}
        <script>window.CODE_MIRROR_GLOBAL_THEME = "{theme_name}";</script>
        {js_links}
    </div>
    """

