import os
import json
import time
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from google import genai
from google.genai import types
from google.cloud import firestore

app = FastAPI(title="VaultShield AI Engine", version="1.0.0")

# Initialize Clients
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
db = firestore.Client()

# In-Memory OTP Store for Demo/Testing (Syncs with Dealer Mobile Dashboard)
ACTIVE_OTPS = {
    "123456": {"vault_id": "VAULT_KADUNA_01", "agent_id": "AGENT_007", "expires_at": time.time() + 300}
}

@app.get("/")
def health_check():
    return {"status": "ACTIVE", "system": "VaultShield AI Cloud Run Core"}

@app.post("/api/v1/verify-and-audit")
async def verify_and_audit(
    vault_id: str = Form(...),
    otp: str = Form(...),
    file: UploadFile = File(...)
):
    """
    1. Validates single-use Dealer OTP
    2. Sends image snapshot to Gemini 2.5 Flash for box/IMEI parsing
    3. Writes structured audit entry to Firestore
    """
    # Step 1: Validate OTP
    otp_entry = ACTIVE_OTPS.get(otp)
    if not otp_entry or otp_entry["vault_id"] != vault_id or time.time() > otp_entry["expires_at"]:
        # Log security flag
        db.collection("security_alerts").add({
            "vault_id": vault_id,
            "type": "UNAUTHORIZED_ACCESS_ATTEMPT",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        raise HTTPException(status_code=403, detail="Invalid or expired OTP code")

    # Step 2: Read image bytes
    image_bytes = await file.read()

    # Step 3: Run Gemini 2.5 Flash Vision Analysis
    prompt = """
    Analyze this camera image captured inside the smart vault slot.
    Extract phone details from the packaging into a clean JSON structure with these keys:
    - manufacturer (e.g., Samsung, Tecno, Apple)
    - model (e.g., Spark 20 Pro, Galaxy A15)
    - storage_capacity (e.g., 128GB, 256GB)
    - imei_number (15-digit IMEI serial number if visible, or "NOT_VISIBLE")
    - slot_occupied (boolean true/false)

    Return ONLY valid JSON.
    """

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        parsed_metadata = json.loads(response.text)
    except Exception as e:
        parsed_metadata = {"error": f"Gemini Parsing Failed: {str(e)}", "slot_occupied": True}

    # Step 4: Write Audit Entry to Firestore
    transaction_ref = db.collection("sales_ledger").document()
    audit_payload = {
        "transaction_id": transaction_ref.id,
        "vault_id": vault_id,
        "agent_id": otp_entry["agent_id"],
        "otp_used": otp,
        "device_info": parsed_metadata,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "APPROVED_DISPATCH"
    }
    transaction_ref.set(audit_payload)

    # Invalidate OTP after single use
    del ACTIVE_OTPS[otp]

    return {
        "status": "APPROVED",
        "message": "Vault lock override authorized for 10s",
        "audit_id": transaction_ref.id,
        "extracted_device": parsed_metadata
    }

