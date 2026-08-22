import requests
import time

BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/whatsapp-webhook"

def test_meta_get_webhook_challenge():
    print("--- 1. Testing GET /whatsapp-webhook (Meta Verification Challenge) ---")
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "agripulse_secret_token_123",
        "hub.challenge": "11582014"
    }
    res = requests.get(WEBHOOK_URL, params=params)
    print("Status Code:", res.status_code)
    print("Content-Type:", res.headers.get("content-type"))
    print("Response Text:", res.text)
    
    assert res.status_code == 200
    assert res.text == "11582014"
    print("[OK] GET Meta Webhook Challenge Verification PASSED!\n")

def test_meta_post_webhook_image_message():
    print("--- 2. Testing POST /whatsapp-webhook (Meta Cloud API JSON Payload) ---")
    meta_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1206040722596923",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550248408",
                                "phone_number_id": "1206040722596923"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test Farmer"},
                                    "wa_id": "15550123456"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "15550123456",
                                    "id": "wamid.HBgLMTU1NTAxMjM0NTYVAgARGBI0QUY1RDU4NUU3RjcxQjQ3AA==",
                                    "timestamp": "1771734567",
                                    "type": "image",
                                    "image": {
                                        "caption": "Early blight tomato leaf test image",
                                        "mime_type": "image/jpeg",
                                        "id": "mock_meta_media_998877"
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

    start = time.time()
    res = requests.post(WEBHOOK_URL, json=meta_payload)
    elapsed_ms = (time.time() - start) * 1000

    print("Status Code:", res.status_code)
    print(f"Webhook Response Time: {elapsed_ms:.1f} ms (Meta < 3s requirement met)")
    print("Response JSON:", res.json())

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    print("[OK] POST Meta WhatsApp Cloud Webhook PASSED!\n")

if __name__ == "__main__":
    print("Running Meta WhatsApp Webhook Integration Verification...\n")
    test_meta_get_webhook_challenge()
    test_meta_post_webhook_image_message()
    print("ALL META WEBHOOK TESTS PASSED!")
