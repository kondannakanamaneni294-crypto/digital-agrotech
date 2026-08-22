import requests
import os
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

models = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "HuggingFaceH4/zephyr-7b-beta"
]

url = "https://router.huggingface.co/hf-inference/v1/chat/completions"

for model in models:
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hello"}],
        "max_tokens": 50
    }
    res = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Model: {model} -> Status: {res.status_code}, Body: {res.text[:120]}")
