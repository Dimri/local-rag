from models.model import load_llm
from unsloth import FastLanguageModel

from .vectordb import search_collection

## globally define and load LLM, tokenizer and embedding model
llm_model, tokenizer = load_llm()
device = "cuda"


def prompt_formatter(query: str, context_items: list[dict]) -> str:
    context = "- " + "\n- ".join([item["text"] for item in context_items])
    base_prompt = """Query: {query}
Context: {context}

You are a highly skilled assistant designed to answer questions based on the provided context. Your response should be in your own words. Your response should be structured in markdown, and you should only use the context that is directly relevant to the query.

Do the following:
- Ensure you fully understand what is being asked in the query.
- Evaluate the provided context and use only the relevant parts to inform your answer. If the context isn't helpful or relevant, do not use it.
- Provide the most concise answer possible. If more explanation is needed, add a follow-up paragraph with further details.
- If you do not know the answer, simply say "I don't know."
- For vague or unclear queries, give a concise, relevant response or clarification of the topic without unnecessary elaboration.

Do not include any pre-text, post-text, or instructions in your final answer. Provide the answer directly, structured in markdown as needed.

Answer:
"""

    base_prompt = base_prompt.format(context=context, query=query)
    # create prompt template for instruction tuned model
    dialogue_template = [
        {
            "role": "system",
            "content": "You are an AI assistant designed for efficient question-answering. Utilize the provided context to formulate a concise answer to the question.",
        },
        {"role": "user", "content": base_prompt},
    ]
    # apply chat template
    prompt = tokenizer.apply_chat_template(
        conversation=dialogue_template, tokenize=False, add_generation_prompt=True
    )
    return prompt


def ask(
    query: str,
    collection,
    temperature: float = 0.7,
    max_new_tokens=512,
    format_answer_text=True,
):
    FastLanguageModel.for_inference(llm_model)
    # get indices and scores of top related results
    context_items = search_collection(query=query, collection=collection)

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

    return output_text, context_items
