# This script is responsible for dynamically injecting the necessary CodeMirror assets
# (CSS and JS links) into the user's Anki card templates. It reads the add-on's
# configuration to determine which note types should have the CodeMirror functionality
# enabled and then modifies their templates accordingly.

from aqt import mw
from bs4 import BeautifulSoup

# Import modules from within the add-on.
from . import asset_manager 
from . import config

# Use the unique prefix from the asset manager to define the ID of the HTML element
# that will be injected. This ensures consistency and avoids conflicts.
INJECTION_ID = f"{asset_manager.PREFIX}resources"

def apply_template_injections():
    """
    The main function that orchestrates the template modification process.
    
    It iterates through every note type (model) in the user's collection. For each one,
    it checks if the add-on is configured to be active. Based on this, it either:
    1. Injects the HTML block containing asset links into the card templates.
    2. Removes a previously injected HTML block if it's no longer needed.
    """
    # Retrieve the user's chosen theme from the configuration.
    global_theme = config.CONFIG.get(config.CONFIG_KEY_GLOBAL_THEME, 'dracula')
    
    # Call the asset manager to generate the complete, self-contained HTML block
    # that links to all necessary CSS and JS files for the reviewer.
    resources_html = asset_manager.get_mobile_resources_html(global_theme)

    # Get the set of note type IDs that the user has selected for injection.
    injected_ids = set(config.CONFIG.get(config.CONFIG_KEY_INJECT_MODELS, []))
    all_models = mw.col.models.all()
    
    # Use Anki's progress bar to provide feedback during this potentially long operation.
    mw.progress.start(max=len(all_models), label="Updating note types...")
    
    something_changed = False
    # Loop through each note type (model) in the collection.
    for i, model in enumerate(all_models):
        mw.progress.update(value=i + 1, label=f"Processing: {model['name']}")
        
        # Determine if the current model *should* have the CodeMirror assets.
        should_have_injection = model['id'] in injected_ids
        model_changed = False

        # Each model can have multiple card templates (e.g., Card 1, Card 2).
        for template in model['tmpls']:
            
            # Process both the front ('qfmt') and back ('afmt') of the card template.
            for key in ['qfmt', 'afmt']:
                # Use BeautifulSoup to safely and easily parse and manipulate the HTML.
                soup = BeautifulSoup(template[key], "html.parser")
                existing_div = soup.find("div", {"id": INJECTION_ID})

                if should_have_injection:
                    # --- ADD OR UPDATE INJECTION ---
                    if existing_div:
                        # If the div already exists, check if it's outdated.
                        # This ensures changes (like a theme update) are applied.
                        if str(existing_div) != resources_html:
                            existing_div.replace_with(BeautifulSoup(resources_html, "html.parser"))
                            model_changed = True
                    else:
                        # If the div doesn't exist, append it to the end of the template.
                        soup.append(BeautifulSoup(resources_html, "html.parser"))
                        model_changed = True
                
                elif not should_have_injection and existing_div:
                    # --- REMOVE INJECTION ---
                    # If the model should not have the injection but the div is found, remove it.
                    existing_div.decompose()
                    model_changed = True
                
                # If any modifications were made, update the template's HTML content.
                if model_changed:
                    template[key] = str(soup)

        # If any of the templates for this model were changed, save the model.
        if model_changed:
            something_changed = True
            mw.col.models.save(model)
            
    mw.progress.finish()
    
    # If any models were updated, a reset is required for changes to take full effect,
    # especially for clearing webview caches.
    if something_changed:
        mw.reset()
