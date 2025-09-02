# Only needed for importing paths

from pathlib import Path
from aqt import mw

# Shared constants for the add-on
ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
ADDON_PATH = Path(mw.addonManager.addonsFolder()) / ADDON_PACKAGE
USER_FILES_PATH = ADDON_PATH / "user_files"
WEB_PATH = f"/_addons/{ADDON_PACKAGE}/user_files"
