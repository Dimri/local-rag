import torch
import pandas as pd
from time import perf_counter as timer
from unsloth import FastLanguageModel
from sentence_transformers import SentenceTransformer, util
from models.model import load_llm
from .embeddings import load_embedding_model


## globally define and load LLM, tokenizer and embedding model
llm_model, tokenizer = load_llm()
embedding_model = load_embedding_model()
device = "cuda"


def prompt_formatter(query: str, context_items: list[dict]) -> str:
    context = "- " + "\n- ".join([item["sentence_chunk"] for item in context_items])
    base_prompt = """Based on the following context items, please answer the query.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer.
Make sure your answers are as explanatory as possible.
Context items:
{context}
\nRelevant passages: <extract relevant passages from the context here>
User Query: {query}
Answer:"""

    base_prompt = base_prompt.format(context=context, query=query)
    # create prompt template for instruction tuned model
    dialogue_template = [
        {
            "role": "system",
            "content": "Give crisp answer followed by an explanantion.\n",
        },
        {"role": "user", "content": base_prompt},
    ]
    # apply chat template
    prompt = tokenizer.apply_chat_template(
        conversation=dialogue_template, tokenize=False, add_generation_prompt=True
    )
    return prompt


def retrieve_relevant_resources(
    query: str,
    embeddings: torch.tensor,
    model: SentenceTransformer = embedding_model,
    n_resources_to_return: int = 5,
    print_time: bool = True,
):
    # embed
    query_embedding = model.encode(query, convert_to_tensor=True)
    query_embedding = query_embedding.to(device)
    # dot product scores
    start_time = timer()
    dot_scores = util.dot_score(query_embedding, embeddings)[0]
    end_time = timer()

    if print_time:
        print(
            f"[INFO] time taken to get scores on {len(embeddings)} embeddings: {end_time - start_time:.6f} seconds"
        )

    scores, indices = torch.topk(input=dot_scores, k=n_resources_to_return)
    return scores, indices


# def print_top_results_and_scores(
#     query: str,
#     embeddings: torch.tensor,
#     pages_and_chunks: list[dict] = pages_and_chunks,
#     n_resources_to_return: int = 5,
# ):
#     top_results_dot_product = retrieve_relevant_resources(query, embeddings)
#     for score, idx in zip(top_results_dot_product[0], top_results_dot_product[1]):
#         print(f"Score: {score:.4f}")
#         print("Text:")
#         print_wrapped(pages_and_chunks[idx]["sentence_chunk"])
#         print(f"Page number: {pages_and_chunks[idx]['page_number']}")
#         print()


def ask(
    query: str,
    embeddings: torch.tensor,
    temperature: float = 0.7,
    max_new_tokens=256,
    format_answer_text=True,
    return_answer_only=True,
):
    FastLanguageModel.for_inference(llm_model)
    # get indices and scores of top related results
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings)

    # read text_chunks_and_embeddings_df from file
    pages_and_chunks = pd.read_csv("text_chunks_and_embeddings_df.csv").to_dict(
        orient="records"
    )

    # create a list of context items
    context_items = [pages_and_chunks[i] for i in indices]

    # add score to context item
    for i, item in enumerate(context_items):
        item["score"] = scores[i].cpu()

    # augmentation
    prompt = prompt_formatter(query=query, context_items=context_items)

    # generation
    input_ids = tokenizer(prompt, return_tensors="pt").to(device)

    # generate an output of tokens
    outputs = llm_model.generate(
        **input_ids, temperature=temperature, max_new_tokens=max_new_tokens
    )

    # decode the tokens into text
    output_text = tokenizer.decode(outputs[0], clean_up_tokenizaton_spaces=True)

    end_header_id = "<|end_header_id|>"
    end_char = output_text.rfind(end_header_id)

    # format the answer
    if format_answer_text:
        # replace the prompt and special tokens
        # output_text = re.sub(re.escape(prompt), "", output_text, flags=re.IGNORECASE)
        output_text = output_text[end_char + len(end_header_id) :].strip()
        output_text = output_text.replace("<|begin_of_text|>", "").replace(
            "<|eot_id|>", ""
        )

    # only return the answer without context items
    if return_answer_only:
        return output_text

    return output_text, context_items
