import gradio as gr
from transformers import TorchAoConfig, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using MPS device")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("Using CUDA device")
else:
    device = torch.device("cpu")
    print("Using CPU device")
quantization_config = TorchAoConfig("int4_weight_only", group_size =128)
model = AutoModelForSeq2SeqLM.from_pretrained(
    "google-t5/t5-base",
    torch_dtype = torch.bfloat16,
    device_map = "auto",
    quantization_config= quantization_config
)
model.to(device)
def translate_text(start,target,text):
    tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-base")
    input_ids = tokenizer((f"translate {start} to {target}: {text}"),return_tensors = "pt").to(device)
    output = model.generate(**input_ids,cache_implementation = "static")
    result = (tokenizer.decode(output[0],skip_special_tokens=True))
    return result
intf = gr.Interface(
fn = translate_text,
inputs = [
gr.Radio(["English"]),
gr.Radio(["French","German"]),
gr.Textbox(label = "Text to translate")],
outputs = "text",
title = "Language Translator with T5",
description = "Translate English to French or German using a quantized T5 Model")
intf.launch()