import torch
from unsloth import FastLanguageModel


def load_llm(model_id="unsloth/Llama-3.2-1B-Instruct-bnb-4bit"):
    llm_model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_id, dtype=None, load_in_4bit=True
    )
    return llm_model, tokenizer


def print_available_gpu_memory():
    gpu_memory_bytes = torch.cuda.get_device_properties(0).total_memory
    gpu_memory_gb = round(gpu_memory_bytes / 1024**3)
    print(f"Available GPU memory: {gpu_memory_gb} GB")
