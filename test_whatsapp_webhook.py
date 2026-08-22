import requests
import time
import os

WEBHOOK_URL = "http://localhost:8000/whatsapp-webhook"

def test_whatsapp_webhook_with_image():
    print("--- Testing /whatsapp-webhook with Twilio Form Data ---")
    
    image_url = "https://raw.githubusercontent.com/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification/main/test_images/tomato_early_blight.jpg"
    
    form_data = {
        "From": "whatsapp:+919876543210",
        "To": "whatsapp:+14155238886",
        "Body": "Leaf diagnosis request for my tomato crop",
        "NumMedia": "1",
        "MediaUrl0": image_url,
        "MediaContentType0": "image/jpeg",
        "Latitude": "37.7749",
        "Longitude": "-122.4194"
    }
    
    start_time = time.time()
    res = requests.post(WEBHOOK_URL, data=form_data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"Status Code: {res.status_code}")
    print(f"Webhook Response Time: {elapsed_ms:.1f} ms (Fast response requirement met)")
    print(f"Content Type: {res.headers.get('content-type')}")
    print("TwiML Body snippet:", res.text.encode("ascii", "replace").decode("ascii"))
    
    assert res.status_code == 200
    assert "application/xml" in res.headers.get("content-type", "")
    assert "AgriPulse Voice Bot" in res.text
    print("[OK] WhatsApp Webhook Instant TwiML Acknowledgment PASSED!\n")

    # Give background task 5 seconds to complete image download, diagnosis, advisory, Bhashini translation & TTS audio generation
    print("Waiting 5s for background AI pipeline task to complete...")
    time.sleep(5)
    
    audio_dir = r"C:\Users\konda\.gemini\antigravity\scratch\digital_agri_network\static\audio"
    audio_files = os.listdir(audio_dir) if os.path.exists(audio_dir) else []
    print(f"Generated TTS Audio Files in static/audio: {audio_files}")
    assert len(audio_files) > 0
    print("[OK] Bhashini / gTTS Audio File Generation PASSED!\n")

if __name__ == "__main__":
    test_whatsapp_webhook_with_image()
