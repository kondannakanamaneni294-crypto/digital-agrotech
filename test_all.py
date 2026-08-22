import os
import sys
from fastapi.testclient import TestClient
from main import app
from utils.weather import fetch_open_meteo_data
from utils.groq_client import generate_farming_advisory

client = TestClient(app)

def test_health():
    print("--- 1. Testing GET /health ---")
    response = client.get("/health")
    print("Status code:", response.status_code)
    print("Response:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("[OK] GET /health PASSED\n")

def test_environment_endpoint():
    print("--- 2. Testing GET /environment (Open-Meteo Integration) ---")
    response = client.get("/environment?lat=37.7749&lon=-122.4194")
    print("Status code:", response.status_code)
    data = response.json()
    print("Response Data:", data)
    assert response.status_code == 200
    assert "temperature_celsius" in data
    assert "soil_moisture_0_to_1cm" in data
    print("[OK] GET /environment PASSED\n")

def test_diagnose_endpoint():
    print("--- 3. Testing POST /diagnose (Hugging Face Inference API) ---")
    image_path = r"C:\Users\konda\.gemini\antigravity\brain\3c6107f1-20af-4974-9615-c696e9b66220\test_plant_leaf_1787330804999.jpg"
    
    if not os.path.exists(image_path):
        print(f"Warning: Image file not found at {image_path}, creating a mock jpeg header.")
        image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"
    else:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
    files = {"file": ("test_leaf.jpg", image_bytes, "image/jpeg")}
    response = client.post("/diagnose", files=files)
    print("Status code:", response.status_code)
    print("Response Data:", response.json())
    assert response.status_code in [200, 503]
    print("[OK] POST /diagnose PASSED\n")

def test_generate_advisory_endpoint():
    print("--- 4. Testing POST /generate-advisory (Groq API) ---")
    payload = {
        "crop_type": "Tomato",
        "crop_status": "Early blight suspected with dark spots on lower leaves",
        "latitude": 37.7749,
        "longitude": -122.4194
    }
    response = client.post("/generate-advisory", json=payload)
    print("Status code:", response.status_code)
    data = response.json()
    print("Advisory Response:")
    print(f"Summary: {data.get('advisory_summary')}")
    print(f"Steps count: {len(data.get('three_step_advisory', []))}")
    for idx, step in enumerate(data.get('three_step_advisory', []), 1):
        print(f"\nStep {idx}: {step.get('title')}")
        print(f"  Action: {step.get('action')}")
        print(f"  Rationale: {step.get('rationale')}")
    assert response.status_code == 200
    assert len(data.get("three_step_advisory", [])) == 3
    print("\n[OK] POST /generate-advisory PASSED\n")


if __name__ == "__main__":
    print("Starting backend tests...\n")
    test_health()
    test_environment_endpoint()
    test_diagnose_endpoint()
    test_generate_advisory_endpoint()
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
