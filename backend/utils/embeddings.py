from .pdf_parser import chunking
from sentence_transformers import SentenceTransformer


def load_embedding_model(model_name="all-mpnet-base-v2"):
    print(f"loading embedding model: {model_name}")
    return SentenceTransformer(model_name_or_path=model_name, device="cuda")


def add_embeddings(pdf_path: str, embedding_model: SentenceTransformer):
    print("inside add_embeddings")
    chunks = chunking(pdf_path)
    for chunk in chunks:
        chunk.metadata["embedding"] = embedding_model.encode(chunk.page_content)
    return chunks


if __name__ == "__main__":
    pass
