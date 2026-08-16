import os
from google import genai
from google.genai import types

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def parse_phone_box_snapshot(image_bytes: bytes) -> str:
    """Uses Gemini Vision API to parse phone packaging details from camera snapshot."""
    prompt = """
    Analyze this camera snapshot inside the smart vault slot.
    Extract the following phone metadata into a clean JSON format:
    - manufacturer (e.g., Samsung, Apple, Tecno)
    - model (e.g., Galaxy A55 5G)
    - storage (e.g., 128GB, 256GB)
    - imei (Extract 15-digit serial number if visible)
    If no box is visible or slot is empty, return {"slot_empty": true}.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return response.text
