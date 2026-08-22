import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")

image_path = r"C:\Users\konda\.gemini\antigravity\brain\3c6107f1-20af-4974-9615-c696e9b66220\test_plant_leaf_1787330804999.jpg"
with open(image_path, "rb") as f:
    image_bytes = f.read()

url = "https://router.huggingface.co/hf-inference/models/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "image/jpeg"
}

print(f"Testing URL: {url}")
res = requests.post(url, headers=headers, data=image_bytes, timeout=15)
print("Status code:", res.status_code)
print("Response JSON:", res.json())
