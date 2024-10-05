import os
import logging
from typing import List

from anki.hooks import addHook
from aqt.editor import Editor
from aqt.utils import showInfo

from . import consult_dict
import threading

filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "app.log")
logging.basicConfig(filename=filename, level=logging.DEBUG)

ADDON_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(ADDON_PATH, "icons", "button.ico")


def paste_word_info(editor: Editor) -> None:
    """ Paste IPA transcription into the IPA field of the Anki editor.

    :param editor: Anki editor window
    """
    note = editor.note
    field_text = note["Word"].lower()
    word = field_text

    # execute the API requests in different threads

    def fetch_word_info(word, note):
        try:
            word_info = consult_dict.consult_free_dict_api(word)
            note["IPA"] = word_info.ipa
            note["Meaning"] = note["Meaning"] + \
                word_info.get_en_meanings_html()
        except Exception:
            logging.error("Failed to get the information of the word '%s'", word)

    def fetch_examples(word, note):
        try:
            examples_html = consult_dict.consult_skell_api(word)
            note["Example"] = note["Example"] + examples_html
        except Exception:
            logging.error("Failed to get the examples of the word '%s'", word)

    def fetch_collocation(word, note):
        try:
            collocation = consult_dict.consult_ozdict_api(word)
            note["Collocation"] = note["Collocation"] + collocation
        except Exception:
            logging.error("Failed to get the collocation of the word '%s'", word)

    threads = [
        threading.Thread(target=fetch_word_info, args=(word, note)),
        threading.Thread(target=fetch_examples, args=(word, note)),
        threading.Thread(target=fetch_collocation, args=(word, note)),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    editor.loadNote()
    editor.web.setFocus()


def on_setup_buttons(buttons: List[str], editor: Editor) -> List[str]:
    """ Add Addon button and Addon combobox to card editor.

    :param buttons: HTML codes of the editor buttons (e.g. for bold, italic, ...)
    :param editor: card editor object
    :return: updated list of buttons
    """
    shortcut_keys = "Ctrl+Shift+Z"
    # add HTML button
    button = editor.addButton(
        ICON_PATH,
        "IPA",
        paste_word_info,
        keys=shortcut_keys,
        tip=f"search word info by ({shortcut_keys})"
    )
    buttons.append(button)
    return buttons


addHook("setupEditorButtons", on_setup_buttons)

# Batch editing
# addHook("browser.setupMenus", batch_adding.setup_menu)
