import requests
from bs4 import BeautifulSoup


class Meaning:
    def __init__(self, part_of_speech: str, definition: str):
        self.part_of_speech = part_of_speech
        self.definition = definition

    def __repr__(self):
        return f"Meaning({self.part_of_speech}, {self.definition})"


class Word:
    def __init__(self, word_str: str, ipa: str, en_meanings: list[Meaning], cn_meanings: list[Meaning],
                 examples: list, synonyms: list, antonyms: list):
        self.word = word_str
        self.ipa = ipa
        self.en_meanings = en_meanings
        self.cn_meanings = cn_meanings
        self.examples = examples
        self.synonyms = synonyms
        self.antonyms = antonyms

    def __repr__(self):
        return f"Word({self.word}, {self.ipa}, {self.en_meanings}, {self.examples}, {self.synonyms}, {self.antonyms})"

    def get_en_meanings_html(self) -> str:
        """
        Get the meanings of the word in English in HTML format
        return: the meanings in HTML format
        """
        html = ""
        # using <ul> to wrap the meanings and replace the special characters
        html += "<ul>"
        for meaning in self.en_meanings:
            html += f"<li>{meaning.part_of_speech}: {meaning.definition}</li>"
        html += "</ul>"
        return html


def consult_free_dict_api(word: str) -> Word:
    """
    Consult the Free Dictionary API to get the word's information
    :param word: the word to consult
    :return: a Word object
    """
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}"

    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Failed to get the information of the word '{word}'")
    json_response = response.json()
    data = json_response[0]

    word = data["word"]

    ipa = None
    # assigm phonetic to ipa if it exists
    if "phonetic" in data:
        ipa = data["phonetic"]
    if not ipa and "phonetics" in data:
        for phonetic in data["phonetics"]:
            if "text" in phonetic:
                if phonetic["text"]:
                    ipa = phonetic["text"]
                    break

    # iterate through the meanings to creat Meaning objects
    en_meanings = []
    for meaning in data["meanings"]:
        part_of_speech = meaning["partOfSpeech"]
        # iterate through the definitions
        for definition in meaning["definitions"]:
            definition_str = definition["definition"]
            meaning_obj = Meaning(part_of_speech, definition_str)
            en_meanings.append(meaning_obj)

    return Word(word, ipa, en_meanings, None, None, None, None)


def handle_html_from_ozdict(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Replace <B> with <br> and lower every tag
    for tag in soup.find_all():
        tag.name = tag.name.lower()
        if tag.name == "tt":
            tag.name = "kbd"
        # remove the a tag
        if tag.name == "a":
            tag.unwrap()
        # add br before the b tag
        if tag.name == "b":
            tag.insert_before(BeautifulSoup("<br>", "html.parser"))
            tag.insert_after(BeautifulSoup("<br>", "html.parser"))
    return str(soup)


def consult_ozdict_api(word: str) -> str:
    """
    Consult the OzDict API to get the word's information
    :param word: the word to consult
    :return: the information of the word
    """
    response = requests.get(
        f"https://ozdic.com/collocation/{word}.txt", timeout=10)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Failed to get the information of the word '{word}' from OzDict")
    origin_html = response.text
    return handle_html_from_ozdict(origin_html)


def consult_skell_api(word: str) -> str:
    response = requests.get(f"https://skell.sketchengine.eu/api/concordance?query={word}&lang=English&format=json", timeout=10)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Failed to get the information of the word '{word}' from Skell")
    data = response.json()

    example_lines = []
    if not data["Lines"]:
        raise requests.exceptions.RequestException(
            f"Failed to get the information of the word '{word}' from Skell")
    for line in data["Lines"]:
        line_str = ""
        left = line["Left"]
        if left and left[0]:
            line_str += left[0]["Str"]
        kwic = line["Kwic"]
        if kwic and kwic[0]:
            line_str += kwic[0]["Str"]
        right = line["Right"]
        if right and right[0]:
            line_str += right[0]["Str"]
        example_lines.append(line_str)
    # return the first 5 examples in thml format using <ul>
    example_html = "<ul>"
    for line in example_lines[:5]:
        example_html += f"<li>{line}</li>"
    example_html += "</ul>"
    return example_html


if __name__ == "__main__":
    test_word = "example"
    word_info = consult_skell_api(test_word)
    print(word_info)
