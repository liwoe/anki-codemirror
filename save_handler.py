# On saving we only want to store the raw code
# 1. This saves a lot of disk space (imagine soring all tags)
# 2. If the user decides to change themes this makes it easy


from bs4 import BeautifulSoup
import base64

def on_editor_will_save_note(problem, note):
    """
    Finds rich CodeMirror blocks and replaces them with a simple,
    lightweight span containing only the raw code and language.
    """
    for field_name, field_value in note.items():
        soup = BeautifulSoup(field_value, "html.parser")
        
        for block in soup.select('.anki-code-block[data-raw-code]'):
            encoded_raw_code = block.get('data-raw-code')
            lang = block.get('data-language', 'python')

            if not encoded_raw_code: continue

            try:
                raw_code = base64.b64decode(encoded_raw_code).decode('utf-8')
                
                # The important part: we store the language in the span
                # Later we will look for codemirror-anki in reviewer_script.js
                simple_span = soup.new_tag(
                    'span', 
                    attrs={
                        'class': 'codemirror-anki', 
                        'data-language': lang,
                    }
                )
                simple_span.string = raw_code
                
                block.replace_with(simple_span)
            except Exception as e:
                print(f"CodeMirror Add-on: Could not process code block on save: {e}")
        
        note[field_name] = str(soup)
    return problem