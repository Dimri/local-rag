import torch
import pandas as pd
from .pdf_parser import chunking
from sentence_transformers import SentenceTransformer


def load_embedding_model(model_name="all-mpnet-base-v2"):
    print(f"loading embedding model: {model_name}")
    return SentenceTransformer(model_name_or_path=model_name, device="cuda")


def create_embeddings_df(pages_and_chunks):
    embedding_model = load_embedding_model()
    print(f"encoding {len(pages_and_chunks)} items.")
    for item in pages_and_chunks:
        item["embedding"] = embedding_model.encode(
            item["sentence_chunk"], convert_to_tensor=True
        ).tolist()
    return pd.DataFrame(pages_and_chunks)


def create_embeddings(pdf_path: str) -> torch.tensor:
    pages_and_chunks = chunking(pdf_path)
    save_path = "text_chunks_and_embeddings_df.csv"
    text_chunks_and_embeddings_df = create_embeddings_df(
        pages_and_chunks=pages_and_chunks
    )
    text_chunks_and_embeddings_df.to_csv(save_path, index=False)

    # change
    # lambda x: torch.tensor(x) TO
    # lambda x: torch.tensor(eval(x))
    # if reading from a csv file.
    text_chunks_and_embeddings_df["embedding"] = text_chunks_and_embeddings_df[
        "embedding"
    ].apply(lambda x: torch.tensor(x))
    return torch.stack(text_chunks_and_embeddings_df["embedding"].to_list())


if __name__ == "__main__":
    from time import perf_counter

    start = perf_counter()
    a = create_embeddings("../data/uploads/State of AI Report - 2024 ONLINE.pdf")
    end = perf_counter()
    print(f"time taken: {end - start:.3f}")
    import code

    code.interact(local=locals())
