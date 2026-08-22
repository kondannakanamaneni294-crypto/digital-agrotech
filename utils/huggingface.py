import requests
from config import settings
from fastapi import HTTPException
import time

def classify_crop_disease(image_bytes: bytes, content_type: str = "image/jpeg", model_id: str = None) -> dict:
    """
    Sends an image file payload to Hugging Face Inference API for crop disease classification.
    """
    if not settings.HF_TOKEN:
        raise HTTPException(status_code=500, detail="Hugging Face API token (HF_TOKEN) is not configured.")
        
    model = model_id or settings.HF_MODEL_ID
    
    # Modern Hugging Face Inference Router endpoint
    primary_url = f"https://router.huggingface.co/hf-inference/models/{model}"
    legacy_url = f"https://api-inference.huggingface.co/models/{model}"
    
    headers = {
        "Authorization": f"Bearer {settings.HF_TOKEN}",
        "Content-Type": content_type if content_type and content_type.startswith("image/") else "image/jpeg"
    }

    max_retries = 3
    for attempt in range(max_retries):
        url = primary_url if attempt < 2 else legacy_url
        try:
            response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            
            if response.status_code == 503:
                error_data = response.json()
                wait_time = error_data.get("estimated_time", 5.0)
                if attempt < max_retries - 1:
                    time.sleep(min(wait_time, 10.0))
                    continue
                else:
                    raise HTTPException(status_code=503, detail=f"Hugging Face model is still loading: {error_data}")

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                predictions = data
                top_prediction = predictions[0].get("label", "Unknown")
                confidence = predictions[0].get("score", 0.0)
                
                return {
                    "status": "success",
                    "model_used": model,
                    "predictions": predictions,
                    "top_prediction": top_prediction,
                    "confidence": confidence
                }
            elif isinstance(data, dict) and "error" in data:
                raise HTTPException(status_code=400, detail=f"Hugging Face API error: {data['error']}")
            else:
                return {
                    "status": "success",
                    "model_used": model,
                    "predictions": [],
                    "top_prediction": "Uncertain classification",
                    "confidence": 0.0,
                    "raw_output": data
                }
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=502, detail=f"Failed to communicate with Hugging Face API: {str(e)}")
            time.sleep(1)
