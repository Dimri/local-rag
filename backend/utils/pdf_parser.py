import re
import fitz
from spacy.lang.en import English


def text_formatter(text: str) -> str:
    cleaned_text = text.replace("\n", " ").strip()
    pattern1 = re.compile(r"#stateofai \| \d")
    pattern2 = re.compile(
        r"Introduction \| Research \| Industry \| Politics \| Safety \| Predictions"
    )
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002700-\U000027BF"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    # remove emojis
    cleaned_text = re.sub(emoji_pattern, "", text)
    # remove commonly occuring patterns
    cleaned_text = re.sub(pattern1, "", cleaned_text)
    cleaned_text = re.sub(pattern2, "", cleaned_text)
    # removed other stuff and made quotes consistent.
    cleaned_text = cleaned_text.replace("→", "")
    cleaned_text = cleaned_text.replace("stateof.ai 2024", "")
    cleaned_text = cleaned_text.replace("’", "'").replace("‘", "'")
    cleaned_text = cleaned_text.replace("“", '"').replace("”", '"')
    return cleaned_text


def open_and_read_pdf(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    pages_and_texts = []
    for page_number, page in enumerate(doc):
        text = page.get_text()
        text = text_formatter(text=text)
        pages_and_texts.append(
            {
                "page_number": page_number,
                "page_char_count": len(text),
                "page_word_count": len(text.split()),
                "page_sentence_count_raw": len(text.split(". ")),
                "page_token_count": len(text) / 4,
                "text": text,
            }
        )
    return pages_and_texts


# function to split list of texts recursively into chunk size
def split_list(input_list: list[str], split_size: int) -> list[list[str]]:
    return [
        input_list[i : i + split_size] for i in range(0, len(input_list), split_size)
    ]


def chunking(pdf_path: str) -> list[dict[str, str]]:
    pages_and_texts = open_and_read_pdf(pdf_path)
    # convert text in to spacy object and extract some stats using spacy
    nlp = English()
    nlp.add_pipe("sentencizer")
    for item in pages_and_texts:
        item["sentences"] = list(nlp(item["text"]).sents)
        item["sentences"] = list(map(str, item["sentences"]))
        item["page_sentence_count_spacy"] = len(item["sentences"])

    # chunking sentences
    num_sentence_chunk_size = 10

    for item in pages_and_texts:
        item["sentence_chunks"] = split_list(
            input_list=item["sentences"], split_size=num_sentence_chunk_size
        )
        item["num_chunks"] = len(item["sentence_chunks"])

    pages_and_chunks = []
    for item in pages_and_texts:
        for sentence_chunk in item["sentence_chunks"]:
            chunk_dict = {}
            chunk_dict["page_number"] = item["page_number"]
            joined_sentence_chunk = " ".join(sentence_chunk).strip()
            chunk_dict["sentence_chunk"] = joined_sentence_chunk
            chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
            chunk_dict["chunk_word_count"] = len(joined_sentence_chunk.split(" "))
            chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4
            pages_and_chunks.append(chunk_dict)

    print("length of pages_and_chunks", len(pages_and_chunks))
    return pages_and_chunks


if __name__ == "__main__":
    pat = open_and_read_pdf("../data/uploads/State of AI Report - 2024 ONLINE.pdf")
    print(pat)
