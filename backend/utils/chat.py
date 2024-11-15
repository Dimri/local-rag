from unsloth import FastLanguageModel
from models.model import load_llm
from .vectordb import search_collection


## globally define and load LLM, tokenizer and embedding model
llm_model, tokenizer = load_llm()
device = "cuda"


def prompt_formatter(query: str, context_items: list[dict]) -> str:
    context = "- " + "\n- ".join([item["text"] for item in context_items])
    base_prompt = """Query: {query} 
Context: {context} 
You are an assistant for question-answering tasks. Use the above pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Keep the answer concise. If you have more to say, first give the consise answer and then add to it in the next paragraph. Do not include any pretext or post-text in the answer.
Answer:"""

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
