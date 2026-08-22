import requests
from config import settings
from fastapi import HTTPException

def get_meta_media_url(media_id: str) -> str:
    """
    Fetches media metadata URL from Meta Graph API using media_id.
    GET https://graph.facebook.com/v20.0/{media_id}
    """
    if not settings.WHATSAPP_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Meta WHATSAPP_ACCESS_TOKEN is not configured.")

    url = f"{settings.META_GRAPH_API_URL}/{media_id}"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        download_url = data.get("url")
        if not download_url:
            raise HTTPException(status_code=400, detail=f"No download URL returned for media_id {media_id}")
        return download_url
    except requests.RequestException as e:
        print(f"[Meta API Error] Failed to fetch media URL for {media_id}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Meta Graph API error: {str(e)}")

def download_meta_media(media_url: str) -> bytes:
    """
    Downloads raw image bytes from Meta's media CDN using Bearer token authentication.
    """
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
    }
    try:
        res = requests.get(media_url, headers=headers, timeout=20)
        res.raise_for_status()
        return res.content
    except requests.RequestException as e:
        print(f"[Meta Media Download Error] Failed downloading media: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Failed to download image from Meta CDN: {str(e)}")

def send_meta_whatsapp_text(recipient_phone: str, text_body: str) -> dict:
    """
    Dispatches a text message back to the sender via Meta Graph API.
    POST https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages
    """
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        print("[Warning] Meta WhatsApp API credentials missing. Simulating response dispatch.")
        print(f"  To: {recipient_phone}")
        print(f"  Text: {text_body[:100]}...")
        return {"status": "simulated", "to": recipient_phone}

    url = f"{settings.META_GRAPH_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Format phone number (remove any + or whatsapp: prefixes if present)
    clean_phone = recipient_phone.replace("whatsapp:", "").replace("+", "").strip()

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": clean_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text_body
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"[Meta WhatsApp Send] Status: {res.status_code} | Body: {res.text[:150]}")
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"[Meta WhatsApp Send Error] Failed sending message: {str(e)}")
        return {"status": "error", "error": str(e)}
