import os
import requests
import uuid
from gtts import gTTS
from config import settings

# Bhashini Pipeline Inference Endpoint
BHASHINI_PIPELINE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

STATIC_AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "audio")
os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)

# Common Agronomic English -> Hindi translation fallback map
AGRI_HINDI_MAP = {
    "Early blight identified with brown spot spots on leaves": "पत्तियों पर भूरे धब्बों के साथ अगेती झुलसा रोग (अर्ली ब्लाइट) की पहचान की गई है।",
    "Grape with Black Rot": "अंगूर में ब्लैक रॉट (काला सड़न) रोग की पहचान की गई है।",
    "Tomato with Early Blight": "टमाटर में अर्ली ब्लाइट (अगेती झुलसा) रोग के लक्षण मिले हैं।",
    "Bell Pepper with Bacterial Spot": "शिमला मिर्च में जीवाणु धब्बा रोग पाया गया है।",
    "Tomato with Septoria Leaf Spot": "टमाटर में सेप्टोरिया लीफ स्पॉट रोग पाया गया है।",
}

def translate_to_hindi(text_en: str) -> str:
    """
    Translates English advisory text into Hindi using Bhashini REST API,
    falling back to gTTS / dictionary translator if Bhashini credentials are unavailable.
    """
    # Check if Bhashini API Key and User ID are configured
    if settings.BHASHINI_API_KEY and settings.BHASHINI_USER_ID and settings.BHASHINI_PIPELINE_ID:
        try:
            headers = {
                "Authorization": settings.BHASHINI_API_KEY,
                "userID": settings.BHASHINI_USER_ID,
                "Content-Type": "application/json"
            }
            
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": "en",
                                "targetLanguage": "hi"
                            },
                            "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text_en
                        }
                    ]
                }
            }
            
            res = requests.post(BHASHINI_PIPELINE_URL, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                data = res.json()
                translated_text = data["pipelineResponse"][0]["output"][0]["target"]
                return translated_text
        except Exception as e:
            print(f"[Warning] Bhashini translation API error ({str(e)}). Using fallback translator.")

    # Dictionary / Rule-based Fallback Translation
    hindi_text = text_en
    for en_phrase, hi_phrase in AGRI_HINDI_MAP.items():
        hindi_text = hindi_text.replace(en_phrase, hi_phrase)
    
    # Simple term translations
    replacements = {
        "3-Step Regenerative Farming Strategy": "3-चरण प्राकृतिक खेती सलाह",
        "Regenerative Protocol": "पुनर्योजी कृषि विधि",
        "Soil Microbiome Inoculation & Organic Matter Maintenance": "मृदा जीवाणु प्रसार एवं जैविक खाद प्रबंधन",
        "Biological Fungal/Bacterial Control & Bio-Foliar Spray": "जैविक कवकनाशी एवं प्राकृतिक पर्णीय छिड़काव",
        "Intercropping & Leguminous Cover Crop Integration": "मिश्रित खेती एवं दलहनी आच्छादन फसल समावेश",
        "Step 1": "चरण 1",
        "Step 2": "चरण 2",
        "Step 3": "चरण 3",
        "Action": "कार्रवाई",
        "Rationale": "कृषि वैज्ञानिक कारण",
        "Tomato": "टमाटर",
        "Wheat": "गेहूं",
        "Corn": "मक्का",
        "Grape": "अंगूर",
        "Rice": "चावल"
    }
    
    for k, v in replacements.items():
        hindi_text = hindi_text.replace(k, v)

    return hindi_text

def text_to_speech_hindi(text_hi: str) -> str:
    """
    Converts Hindi text to audio speech file (.mp3) using Bhashini TTS or gTTS.
    Returns the relative static URL path for the generated audio file.
    """
    filename = f"advisory_{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(STATIC_AUDIO_DIR, filename)

    # Check if Bhashini TTS API is configured
    if settings.BHASHINI_API_KEY and settings.BHASHINI_USER_ID and settings.BHASHINI_PIPELINE_ID:
        try:
            headers = {
                "Authorization": settings.BHASHINI_API_KEY,
                "userID": settings.BHASHINI_USER_ID,
                "Content-Type": "application/json"
            }
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {"sourceLanguage": "hi"},
                            "gender": "female"
                        }
                    }
                ],
                "inputData": {
                    "input": [{"source": text_hi}]
                }
            }
            res = requests.post(BHASHINI_PIPELINE_URL, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                import base64
                data = res.json()
                audio_b64 = data["pipelineResponse"][0]["audio"][0]["audioContent"]
                audio_bytes = base64.b64decode(audio_b64)
                with open(filepath, "wb") as f:
                    f.write(audio_bytes)
                return f"/static/audio/{filename}"
        except Exception as e:
            print(f"[Warning] Bhashini TTS API error ({str(e)}). Using gTTS fallback engine.")

    # High-quality gTTS Fallback Engine
    try:
        tts = gTTS(text=text_hi, lang='hi', slow=False)
        tts.save(filepath)
        return f"/static/audio/{filename}"
    except Exception as e:
        print(f"[Error] Failed to generate TTS audio: {str(e)}")
        return ""
