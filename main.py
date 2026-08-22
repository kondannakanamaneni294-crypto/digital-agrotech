import os
import requests
from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Form, BackgroundTasks, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from schemas import (
    EnvironmentData, 
    DiagnosisResponse, 
    AdvisoryRequest, 
    AdvisoryResponse
)
from config import settings
from utils.weather import fetch_open_meteo_data
from utils.huggingface import classify_crop_disease
from utils.groq_client import generate_farming_advisory
from utils.bhashini import translate_to_hindi, text_to_speech_hindi
from utils.twilio_client import send_whatsapp_message
from utils.meta_whatsapp import get_meta_media_url, download_meta_media, send_meta_whatsapp_text

app = FastAPI(
    title="Digital Agriculture Network API & WhatsApp Cloud Bot",
    description="Interoperable FastAPI backend supporting Meta Official WhatsApp Cloud API, Open-Meteo, Hugging Face crop diagnosis, Groq advisory, and Bhashini multilingual TTS.",
    version="3.0.0"
)

# CORS Middleware Setup
# For initial testing & development, allow all origins ("*").
# PRODUCTION DEPLOYMENT SECURITY:
# When deployed to Render/Vercel, replace ["*"] with your specific frontend Vercel URL, e.g.:
# allow_origins=["https://digital-agri-network.vercel.app", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files for serving generated TTS audio files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return {
        "network": "Digital Agriculture Interoperability Network & Meta WhatsApp Cloud Bot",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": {
            "environment": "GET /environment?lat={lat}&lon={lon}",
            "diagnose": "POST /diagnose (Form-data: file)",
            "generate_advisory": "POST /generate-advisory (JSON body)",
            "whatsapp_webhook_get": "GET /whatsapp-webhook (Meta Hub Challenge Verification)",
            "whatsapp_webhook_post": "POST /whatsapp-webhook (Meta JSON & Twilio Form-Data Webhook)"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/environment", response_model=EnvironmentData)
def get_environment_data(
    lat: float = Query(..., description="Latitude of the farm location"),
    lon: float = Query(..., description="Longitude of the farm location")
):
    """Fetch current real-time temperature and soil moisture from Open-Meteo API."""
    data = fetch_open_meteo_data(lat, lon)
    return data

@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_crop_disease(file: UploadFile = File(...)):
    """Accepts an uploaded image file of a crop leaf and classifies disease via Hugging Face API."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    diagnosis = classify_crop_disease(image_bytes, content_type=file.content_type)
    return diagnosis

@app.post("/generate-advisory", response_model=AdvisoryResponse)
def generate_advisory(payload: AdvisoryRequest):
    """Constructs prompt from crop status & environment data, then calls Groq for 3-step advisory."""
    temp_celsius = payload.temperature_celsius
    soil_moisture = payload.soil_moisture
    lat = payload.latitude
    lon = payload.longitude

    if (lat is not None and lon is not None) and (temp_celsius is None or soil_moisture is None):
        try:
            weather = fetch_open_meteo_data(lat, lon)
            if temp_celsius is None:
                temp_celsius = weather.get("temperature_celsius")
            if soil_moisture is None:
                soil_moisture = weather.get("soil_moisture_0_to_1cm")
        except Exception:
            pass

    advisory = generate_farming_advisory(
        crop_type=payload.crop_type,
        crop_status=payload.crop_status,
        temp_celsius=temp_celsius,
        soil_moisture=soil_moisture,
        lat=lat,
        lon=lon
    )

    return advisory

# --- META WHATSAPP CLOUD API VERIFICATION ENDPOINT (GET) ---
@app.get("/whatsapp-webhook")
def verify_meta_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    GET /whatsapp-webhook: Meta WhatsApp Cloud API Webhook Challenge Verification.
    If hub.mode == 'subscribe' and hub.verify_token matches WHATSAPP_VERIFY_TOKEN,
    returns int(hub.challenge) / plain text challenge with HTTP 200 OK.
    """
    print(f"[Meta Webhook Challenge] mode: {hub_mode} | token: {hub_verify_token} | challenge: {hub_challenge}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        print("[Meta Webhook Challenge] Verified successfully!")
        return Response(content=str(hub_challenge), media_type="text/plain", status_code=200)
    
    raise HTTPException(status_code=403, detail="Verification token mismatch.")

# --- ASYNCHRONOUS META PIPELINE WORKER ---
def process_meta_whatsapp_pipeline(
    from_number: str,
    media_id: str = None,
    text_body: str = None,
    lat: float = 37.7749,
    lon: float = -122.4194
):
    """
    Asynchronously processes incoming Meta WhatsApp messages:
    1. Fetches and downloads image bytes from Meta Graph API using media_id (if present)
    2. Runs Hugging Face disease classification
    3. Fetches live Open-Meteo weather data
    4. Generates 3-step regenerative farming advisory (Groq / Agronomic engine)
    5. Dispatches formatted WhatsApp text advisory back to sender via Meta Graph API
    """
    print(f"\n[Meta Pipeline] Processing message from {from_number}...")
    crop_status = text_body or "Crop disease check requested via leaf image upload"
    crop_type = "Tomato"

    # Step 1: Handle Media ID Download from Meta Graph API
    if media_id:
        try:
            print(f"[Meta Pipeline] Resolving media URL for media_id: {media_id}")
            media_url = get_meta_media_url(media_id)
            print(f"[Meta Pipeline] Downloading image bytes from Meta CDN...")
            image_bytes = download_meta_media(media_url)
            
            diagnosis = classify_crop_disease(image_bytes, content_type="image/jpeg")
            top_pred = diagnosis.get("top_prediction", "Unknown plant condition")
            confidence = diagnosis.get("confidence", 0.0) * 100
            crop_status = f"{top_pred} (Identified with {confidence:.1f}% confidence)"
            print(f"[Meta Pipeline] Diagnosis complete: {crop_status}")
        except Exception as e:
            print(f"[Meta Pipeline Error] Failed to process image: {str(e)}")

    # Step 2: Fetch Live Open-Meteo Weather Data
    temp_celsius = 22.0
    soil_moisture = 0.25
    try:
        weather = fetch_open_meteo_data(lat, lon)
        temp_celsius = weather.get("temperature_celsius", 22.0)
        soil_moisture = weather.get("soil_moisture_0_to_1cm", 0.25)
    except Exception:
        pass

    # Step 3: Generate 3-Step Advisory
    advisory_data = generate_farming_advisory(
        crop_type=crop_type,
        crop_status=crop_status,
        temp_celsius=temp_celsius,
        soil_moisture=soil_moisture,
        lat=lat,
        lon=lon
    )

    steps = advisory_data.get("three_step_advisory", [])

    # Step 4: Construct Formatted Advisory Text
    reply_text = f"🌱 *AgriPulse Regenerative Advisory for {crop_type}*\n"
    reply_text += f"━━━━━━━━━━━━━━━━━━━━━\n"
    reply_text += f"🔍 *Pathology:* {crop_status}\n"
    reply_text += f"🌡️ *Live Weather:* {temp_celsius}°C | 💧 *Soil Moisture:* {soil_moisture} m³/m³\n\n"
    reply_text += f"📋 *3-Step Regenerative Action Protocol:*\n\n"

    for idx, step in enumerate(steps, 1):
        reply_text += f"*[Step {idx}: {step.get('title')}]*\n"
        reply_text += f"• *Action:* {step.get('action')}\n"
        reply_text += f"• *Agronomic Rationale:* _{step.get('rationale')}_\n\n"

    reply_text += f"ℹ️ _Powered by AgriPulse Interoperable Network_"

    # Step 5: Send Text Message back to Sender via Meta Graph API
    print(f"[Meta Pipeline] Sending WhatsApp message to {from_number} via Meta Graph API...")
    send_meta_whatsapp_text(recipient_phone=from_number, text_body=reply_text)
    print("[Meta Pipeline] Completed successfully!\n")

# --- META WHATSAPP CLOUD API WEBHOOK ENDPOINT (POST) ---
@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    POST /whatsapp-webhook: Handles incoming webhooks from Meta Official WhatsApp Cloud API
    (as well as legacy Twilio Form-Data requests). Parses payloads and processes asynchronously.
    """
    content_type = request.headers.get("content-type", "")

    # 1. Handle Meta WhatsApp Cloud API JSON Payloads
    if "application/json" in content_type:
        try:
            body = await request.json()
            print(f"[Meta Webhook Received] Payload object: {body.get('object')}")

            entries = body.get("entry", [])
            for entry in entries:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    for msg in messages:
                        from_number = msg.get("from")
                        msg_type = msg.get("type")
                        
                        media_id = None
                        text_body = None

                        if msg_type == "image":
                            media_id = msg.get("image", {}).get("id")
                            text_body = msg.get("image", {}).get("caption")
                        elif msg_type == "text":
                            text_body = msg.get("text", {}).get("body")

                        if from_number:
                            background_tasks.add_task(
                                process_meta_whatsapp_pipeline,
                                from_number=from_number,
                                media_id=media_id,
                                text_body=text_body
                            )

            # Return immediate HTTP 200 OK to Meta
            return {"status": "ok"}
        except Exception as e:
            print(f"[Meta Webhook Error] JSON parsing failed: {str(e)}")
            return {"status": "ok"}

    # 2. Handle Twilio Form Data Webhook Payloads (Backwards Compatibility)
    else:
        form_data = await request.form()
        from_number = form_data.get("From")
        media_url = form_data.get("MediaUrl0")
        num_media = int(form_data.get("NumMedia", 0))
        text_body = form_data.get("Body")

        if from_number:
            background_tasks.add_task(
                process_whatsapp_pipeline,
                from_number=from_number,
                media_url=media_url if num_media > 0 else None,
                text_body=text_body
            )

        twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>🌱 *AgriPulse Voice Bot*: Crop telemetry & leaf diagnosis received!</Message>
</Response>"""
        return Response(content=twiml_response, media_type="application/xml")

# Legacy Twilio pipeline helper retained for backwards compatibility
def process_whatsapp_pipeline(
    from_number: str,
    media_url: str = None,
    text_body: str = None,
    lat: float = 37.7749,
    lon: float = -122.4194
):
    print(f"\n[Twilio Bot] Processing pipeline for {from_number}...")
    crop_status = text_body or "Crop condition check requested via image upload"
    crop_type = "Tomato"

    if media_url:
        try:
            auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN) if settings.TWILIO_ACCOUNT_SID else None
            img_res = requests.get(media_url, auth=auth, timeout=15)
            if img_res.status_code == 200:
                diagnosis = classify_crop_disease(img_res.content, content_type="image/jpeg")
                top_pred = diagnosis.get("top_prediction", "Unknown plant disease")
                confidence = diagnosis.get("confidence", 0.0) * 100
                crop_status = f"{top_pred} (Identified with {confidence:.1f}% confidence)"
        except Exception as e:
            print(f"[Twilio Bot Error] Image diagnosis failed: {str(e)}")

    temp_celsius = 22.0
    soil_moisture = 0.25
    try:
        weather = fetch_open_meteo_data(lat, lon)
        temp_celsius = weather.get("temperature_celsius", 22.0)
        soil_moisture = weather.get("soil_moisture_0_to_1cm", 0.25)
    except Exception:
        pass

    advisory_data = generate_farming_advisory(
        crop_type=crop_type,
        crop_status=crop_status,
        temp_celsius=temp_celsius,
        soil_moisture=soil_moisture,
        lat=lat,
        lon=lon
    )

    steps = advisory_data.get("three_step_advisory", [])

    english_text = f"🌱 *Digital Agriculture Advisory for {crop_type}*\n"
    english_text += f"*Diagnosis:* {crop_status}\n"
    english_text += f"*Weather:* {temp_celsius}°C | Soil Moisture: {soil_moisture} m³/m³\n\n"
    
    for idx, step in enumerate(steps, 1):
        english_text += f"*Step {idx}: {step.get('title')}*\n"
        english_text += f"• Action: {step.get('action')}\n"
        english_text += f"• Rationale: {step.get('rationale')}\n\n"

    hindi_text = translate_to_hindi(english_text)
    audio_path = text_to_speech_hindi(hindi_text)
    
    audio_url = ""
    if audio_path:
        base_url = settings.PUBLIC_BASE_URL.rstrip('/')
        audio_url = f"{base_url}{audio_path}"

    reply_body = f"🌾 *डिजिटल कृषि सलाह (Hindi Advisory)* 🌾\n\n{hindi_text}"
    send_whatsapp_message(to_whatsapp_number=from_number, text_body=reply_body, media_url=audio_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
