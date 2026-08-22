import requests
from config import settings
from fastapi import HTTPException

def fetch_open_meteo_data(latitude: float, longitude: float) -> dict:
    """
    Utility function to fetch current temperature and soil moisture 
    from the Open-Meteo API based on latitude and longitude.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm"
    }
    
    try:
        response = requests.get(settings.OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        units = data.get("current_units", {})
        
        return {
            "latitude": data.get("latitude", latitude),
            "longitude": data.get("longitude", longitude),
            "temperature_celsius": current.get("temperature_2m"),
            "soil_moisture_0_to_1cm": current.get("soil_moisture_0_to_1cm"),
            "soil_moisture_1_to_3cm": current.get("soil_moisture_1_to_3cm"),
            "units": units
        }
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, 
            detail=f"Failed to fetch data from Open-Meteo API: {str(e)}"
        )
