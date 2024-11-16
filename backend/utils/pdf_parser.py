import re
import pymupdf4llm
import emoji
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def remove_emoji(string):
    return emoji.replace_emoji(string, replace="")


def remove_repeated_substring(text):
    pattern = re.compile(r"[#-]{3,}|\s{3,}")
    return pattern.sub(repl="", string=text)


def text_formatter(text: str) -> str:
    # remove newlines.
    cleaned_text = text.replace("\n", " ").strip()
    # remove emojis
    cleaned_text = remove_emoji(cleaned_text)
    return cleaned_text


def open_and_read_pdf(pdf_path: str) -> list[dict]:
    md_doc: list[dict] = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
    pages_and_texts = []
    for doc in md_doc:
        page_number = doc["metadata"]["page"]
        text = doc["text"]
        text = text_formatter(text=text)
        pages_and_texts.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages_and_texts


def chunking(pdf_path: str, chunk_size: int = 250, chunk_overlap: int = 30):
    pages_and_texts = open_and_read_pdf(pdf_path)
    # chunking sentences
    headers_to_split_on = [("#" * i, f"Header {i}") for i in range(1, 7)]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on, strip_headers=False
    )

    # split the markdown file, page by page
    md_header_splits = []
    for dct in pages_and_texts:
        md_splits = markdown_splitter.split_text(dct["text"])
        for doc in md_splits:
            doc.metadata["page_number"] = dct["page_number"]
        md_header_splits.extend(md_splits)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    # Split
    splits = text_splitter.split_documents(md_header_splits)
    print(f"{type(splits[0]) = }")
    # process the chunks
    # remove chunks with char count less than 20
    # strip chunks
    # remove repeating symbols, whitespace from each split
    for split in splits:
        split.page_content = remove_repeated_substring(split.page_content)
        split.page_content = split.page_content.strip()
    splits = [split for split in splits if len(split.page_content) > 20]
    return splits


if __name__ == "__main__":
    pat = open_and_read_pdf("../data/uploads/State of AI Report - 2024 ONLINE.pdf")
    print(pat)
