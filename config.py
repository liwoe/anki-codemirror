# Not interesting just loading and saving configs...

from aqt import mw

ADDON_IDENTIFIER = None
CONFIG = {}

# UPDATED: We only need one key for the theme.
CONFIG_KEY_GLOBAL_THEME = "global_theme"
CONFIG_KEY_INJECT_MODELS = "injected_model_ids"
CONFIG_KEY_BYPASS_MODELS = "bypassed_model_ids"

def load_config():
    """Loads the addon's configuration from disk."""
    global ADDON_IDENTIFIER, CONFIG
    
    ADDON_IDENTIFIER = mw.addonManager.addonFromModule(__name__)
    if not ADDON_IDENTIFIER:
        CONFIG = {
            CONFIG_KEY_GLOBAL_THEME: "dracula",
            CONFIG_KEY_INJECT_MODELS: [],
            CONFIG_KEY_BYPASS_MODELS: [],
        }
        return

    loaded_config = mw.addonManager.getConfig(ADDON_IDENTIFIER) or {}
    
    # Set defaults for any missing keys
    CONFIG.setdefault(CONFIG_KEY_GLOBAL_THEME, "dracula")
    CONFIG.setdefault(CONFIG_KEY_INJECT_MODELS, [])
    CONFIG.setdefault(CONFIG_KEY_BYPASS_MODELS, [])
    
    CONFIG.update(loaded_config)

def save_config():
    """Saves the current CONFIG dictionary to disk."""
    if ADDON_IDENTIFIER:
        mw.addonManager.writeConfig(ADDON_IDENTIFIER, CONFIG)