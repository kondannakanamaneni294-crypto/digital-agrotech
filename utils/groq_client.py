import requests
import json
import re
from config import settings
from fastapi import HTTPException

GROQ_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_fallback_advisory(
    crop_type: str,
    crop_status: str,
    temp_celsius: float = None,
    soil_moisture: float = None,
    lat: float = None,
    lon: float = None
) -> dict:
    """
    Algorithmic agronomic fallback to construct a 3-step regenerative farming advisory 
    when the external LLM key is invalid or unavailable.
    """
    temp_val = temp_celsius if temp_celsius is not None else 22.0
    moisture_val = soil_moisture if soil_moisture is not None else 0.20

    # Step 1: Soil & Water Management based on soil moisture
    if moisture_val < 0.15:
        step1_title = "Regenerative Soil Moisture Restoration & Mulching"
        step1_action = f"Apply a 3-inch layer of organic compost or straw mulch around the root zones of the {crop_type} crop and introduce low-pressure drip fertigation with compost tea."
        step1_rationale = f"Soil moisture level ({moisture_val:.3f} m³/m³) is below optimal threshold. Mulching reduces evaporation, stabilizes soil temperature, and builds soil organic matter (SOM)."
    elif moisture_val > 0.35:
        step1_title = "Aeration, Drainage Improvement & Biochar Application"
        step1_action = f"Incorporate coarse biochar and construct shallow drainage swales around {crop_type} beds to improve infiltration and prevent root hypoxia."
        step1_rationale = f"Elevated soil moisture ({moisture_val:.3f} m³/m³) creates anaerobic conditions favorable for soil-borne pathogens; biochar improves pore structure without chemical inputs."
    else:
        step1_title = "Soil Microbiome Inoculation & Organic Matter Maintenance"
        step1_action = f"Apply indigenous microorganism (IMO) inoculant combined with liquid humic acids directly to the root zone of {crop_type}."
        step1_rationale = f"Current soil moisture ({moisture_val:.3f} m³/m³) is ideal for microbial proliferation, supporting mycorrhizal nutrient exchange."

    # Step 2: Crop Protection / Disease Mitigation based on crop_status and temp
    if "blight" in crop_status.lower() or "rot" in crop_status.lower() or "spot" in crop_status.lower():
        step2_title = "Biological Fungal/Bacterial Control & Bio-Foliar Spray"
        step2_action = f"Apply a foliar spray of Bacillus subtilis or Trichoderma harzianum combined with a 0.5% neem oil emulsion early in the morning."
        step2_rationale = f"Active disease indicators ('{crop_status}') require competitive biological suppression to suppress pathogenic spore germination without harming beneficial insects."
    else:
        step2_title = "Natural Plant Immunity Booster & Foliar Silica"
        step2_action = f"Foliar spray liquid kelp extract (Ascophyllum nodosum) and soluble silicon to strengthen plant cell walls."
        step2_rationale = f"Proactive chitin and silica enhancement increases physical leaf resistance against stress and potential infection under current ambient temp ({temp_val:.1f} °C)."

    # Step 3: Biodiverse Cover Cropping & Nutrient Cycling
    step3_title = "Intercropping & Leguminous Cover Crop Integration"
    step3_action = f"Sow a companion cover crop mixture of Crimson Clover and Hairy Vetch between {crop_type} rows."
    step3_rationale = "Leguminous cover crops fix atmospheric nitrogen biologically, enhance soil carbon sequestration, and continuously feed soil microbiology."

    summary = (
        f"3-Step Regenerative Farming Strategy for {crop_type} experiencing '{crop_status}' "
        f"at ambient temperature {temp_val:.1f} °C and soil moisture {moisture_val:.3f} m³/m³."
    )

    return {
        "status": "success",
        "crop_type": crop_type,
        "crop_status": crop_status,
        "environment_summary": {
            "temperature_celsius": temp_celsius,
            "soil_moisture": soil_moisture,
            "latitude": lat,
            "longitude": lon
        },
        "advisory_summary": summary,
        "three_step_advisory": [
            {
                "step_number": 1,
                "title": step1_title,
                "action": step1_action,
                "rationale": step1_rationale
            },
            {
                "step_number": 2,
                "title": step2_title,
                "action": step2_action,
                "rationale": step2_rationale
            },
            {
                "step_number": 3,
                "title": step3_title,
                "action": step3_action,
                "rationale": step3_rationale
            }
        ]
    }

def generate_farming_advisory(
    crop_type: str,
    crop_status: str,
    temp_celsius: float = None,
    soil_moisture: float = None,
    lat: float = None,
    lon: float = None
) -> dict:
    """
    Constructs a prompt based on crop status and environmental parameters,
    and calls the Groq API to produce a 3-step regenerative farming advisory.
    Falls back to rules-based agronomic advisory if Groq API key is invalid/unavailable.
    """
    if not settings.GROQ_API_KEY:
        return generate_fallback_advisory(crop_type, crop_status, temp_celsius, soil_moisture, lat, lon)

    temp_str = f"{temp_celsius} °C" if temp_celsius is not None else "Not provided"
    moisture_str = f"{soil_moisture} m³/m³" if soil_moisture is not None else "Not provided"
    location_str = f"Latitude {lat}, Longitude {lon}" if (lat is not None and lon is not None) else "Not provided"

    system_prompt = (
        "You are an expert regenerative agriculture specialist and agronomics advisor. "
        "Your role is to assess crop condition along with environmental conditions (temperature and soil moisture) "
        "and provide an actionable, science-based 3-step regenerative farming advisory. "
        "You MUST respond ONLY with a valid JSON object matching the requested schema."
    )

    user_prompt = f"""
Crop Type: {crop_type}
Crop Condition / Diagnosis: {crop_status}
Environmental Parameters:
- Temperature: {temp_str}
- Soil Moisture: {moisture_str}
- Location: {location_str}

Return a valid JSON object strictly matching this schema:
{{
  "summary": "Brief 1-2 sentence overview of the regenerative action strategy.",
  "steps": [
    {{
      "step_number": 1,
      "title": "Title for Step 1",
      "action": "Specific regenerative practice action",
      "rationale": "Agronomic reasoning based on current temp, soil moisture, and crop health"
    }},
    {{
      "step_number": 2,
      "title": "Title for Step 2",
      "action": "Specific action",
      "rationale": "Agronomic reasoning"
    }},
    {{
      "step_number": 3,
      "title": "Title for Step 3",
      "action": "Specific action",
      "rationale": "Agronomic reasoning"
    }}
  ]
}}
"""

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GROQ_MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(GROQ_COMPLETIONS_URL, headers=headers, json=payload, timeout=25)
        
        if response.status_code == 401:
            print("[Warning] Groq API returned 401 Invalid Key. Falling back to agronomic engine.")
            return generate_fallback_advisory(crop_type, crop_status, temp_celsius, soil_moisture, lat, lon)

        response.raise_for_status()
        data = response.json()
        
        content = data["choices"][0]["message"]["content"]
        
        try:
            parsed_json = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                parsed_json = json.loads(match.group(0))
            else:
                return generate_fallback_advisory(crop_type, crop_status, temp_celsius, soil_moisture, lat, lon)

        return {
            "status": "success",
            "crop_type": crop_type,
            "crop_status": crop_status,
            "environment_summary": {
                "temperature_celsius": temp_celsius,
                "soil_moisture": soil_moisture,
                "latitude": lat,
                "longitude": lon
            },
            "advisory_summary": parsed_json.get("summary", "3-Step Regenerative Farming Advisory"),
            "three_step_advisory": parsed_json.get("steps", [])
        }

    except requests.RequestException as e:
        print(f"[Warning] Groq request failed ({str(e)}). Using fallback advisory generator.")
        return generate_fallback_advisory(crop_type, crop_status, temp_celsius, soil_moisture, lat, lon)
