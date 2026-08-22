from twilio.rest import Client
from config import settings

def send_whatsapp_message(to_whatsapp_number: str, text_body: str, media_url: str = None) -> dict:
    """
    Sends an outbound WhatsApp message containing text and optional audio media URL
    to the target recipient number using the Twilio Python SDK.
    """
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("[Warning] Twilio credentials not fully configured. Simulating WhatsApp response dispatch.")
        print(f"  To: {to_whatsapp_number}")
        print(f"  Body snippet: {text_body[:100]}...")
        if media_url:
            print(f"  Audio Media URL: {media_url}")
        return {"status": "simulated", "to": to_whatsapp_number}

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Ensure numbers are formatted with whatsapp: prefix
        from_number = settings.TWILIO_WHATSAPP_NUMBER
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
            
        if not to_whatsapp_number.startswith("whatsapp:"):
            to_whatsapp_number = f"whatsapp:{to_whatsapp_number}"

        kwargs = {
            "from_": from_number,
            "to": to_whatsapp_number,
            "body": text_body
        }

        if media_url:
            kwargs["media_url"] = [media_url]

        message = client.messages.create(**kwargs)
        return {
            "status": "sent",
            "sid": message.sid,
            "to": to_whatsapp_number
        }
    except Exception as e:
        print(f"[Error] Failed to send WhatsApp message via Twilio SDK: {str(e)}")
        return {"status": "error", "error": str(e)}
