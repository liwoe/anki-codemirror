# This file is needed for bypassing ankis cloze error message
# when creating codemirror clozes the html will look like this:
# {{<span class="cm-variable">c1</span>::<span class="cm-variable">cloze</span>}}
# Anki cant handle the html tags between that it can only handle it like this 
# <example>{{c1::cloze}}</example>
# Therfore a bypass is needed.

from anki.notes import Note, NoteFieldsCheckResult
from . import config

_original_fields_check = None

def bypassed_fields_check(note_instance: Note) -> NoteFieldsCheckResult:
    """
    If the note's type is in our bypass list, it immediately returns NORMAL.
    Otherwise, it performs the original check.
    This is called monkey patching. 
    (Unfortunately monkey patching is not good and can break if anki updates...)
    """
    # Read directly from the global CONFIG dictionary using the new key
    bypassed_ids = config.CONFIG.get(config.CONFIG_KEY_BYPASS_MODELS, [])

    if note_instance.mid in bypassed_ids:
        return NoteFieldsCheckResult.NORMAL

    # Call the original Anki function
    if _original_fields_check:
        return _original_fields_check(note_instance)
    
    return Note.fields_check(note_instance) # Fallback

def apply_field_check_patch():
    """Applies the monkey patch to Note.fields_check."""
    global _original_fields_check
    if not hasattr(Note, '_fields_check_original_codemirror'):
        _original_fields_check = Note.fields_check
        Note._fields_check_original_codemirror = _original_fields_check
        Note.fields_check = bypassed_fields_check