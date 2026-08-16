import os
import json
from google import genai
from google.genai import types

class GeminiVisionService:
    """Wrapper for Google Gemini 2.5 Flash multi-modal vision API calls."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def extract_device_metadata(self, image_bytes: bytes) -> dict:
        """Uses Gemini Vision API to run OCR and extract phone packaging specifications."""
        if not self.client:
            return {"error": "GEMINI_API_KEY environment variable missing", "slot_occupied": True}

        prompt = """
        Analyze this camera image taken inside a smart vault slot.
        Extract the following device details from the box packaging into a clean JSON structure:
        - manufacturer (e.g., Samsung, Tecno, Apple, Xiaomi)
        - model (e.g., Spark 20 Pro, Galaxy A15)
        - storage_capacity (e.g., 128GB, 256GB)
        - imei_number (15-digit serial string if printed on packaging, or "NOT_VISIBLE")
        - slot_occupied (boolean true if phone box present, false if slot is empty)

        Return ONLY valid JSON.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {
                "error": f"Gemini Parsing Error: {str(e)}",
                "slot_occupied": True,
                "imei_number": "UNREADABLE"
            }

gemini_service = GeminiVisionService()
