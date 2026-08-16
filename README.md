# vaultshield-ai
VaultShield AI is an AI-powered smart vault and zero-trust risk management platform protecting smartphone credit dealers from agent fraud, untracked dispatches, and physical inventory loss.
# VaultShield AI 🛡️📱

> **Smart IoT Vault & Zero-Trust Physical Inventory Control for Smartphone Credit Dealers**

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?style=flat&logo=googlecloud)](https://cloud.google.com/run)
[![Gemini API](https://img.shields.io/badge/AI-Gemini_2.5_Flash-8E75B2?style=flat&logo=googlegemini)](https://ai.google.dev/)
[![Hardware](https://img.shields.io/badge/Hardware-Raspberry_Pi_4-C51A4A?style=flat&logo=raspberrypi)](https://www.raspberrypi.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Problem & Overview

In emerging markets, Buy-Now-Pay-Later (BNPL) and smartphone credit financing are critical for expanding digital and financial inclusion. However, primary dealers who supply high-value devices to remote sales agents face severe **inventory shrinkage, untracked dispatches, and agent fraud**. 

Traditional device-locking solutions operate *after* a buyer defaults on payments, leaving dealers completely exposed *before* the device leaves the physical kiosk.

**VaultShield AI** solves the principal-agent problem by establishing a zero-trust physical security layer. Remote agent kiosks are locked inside an IoT smart vault. Unlocking requires a real-time single-use OTP approved by the dealer. Upon access, an internal camera captures the event and utilizes the **Gemini 2.5 Flash Vision API** to perform optical character recognition (OCR) on the phone box—extracting the IMEI, model, manufacturer, and serial numbers instantly to write an immutable record to the ledger.

---

## 🏗️ System Architecture

```text
               +-------------------------------------------------+
               |                REMOTE AGENT KIOSK               |
               |                                                 |
               |  [Agent Web App] ---> Input OTP                 |
               |         |                                       |
               |  [Raspberry Pi 4]                               |
               |     ├── Electronic Solenoid Lock (GPIO 18)      |
               |     └── Interior CSI/USB Camera Module          |
               +------------------------+------------------------+
                                        |
                             HTTPS / JSON Payload + JPG
                                        |
                                        v
               +-------------------------------------------------+
               |              GOOGLE CLOUD INFRASTRUCTURE        |
               |                                                 |
               |  [Google Cloud Run Microservice (FastAPI)]      |
               |         │                                       |
               |         ├── 1. Validate Dealer OTP              |
               |         ├── 2. Process Image via Gemini API     |
               |         └── 3. Execute Zero-Trust Risk Engine   |
               |                                                 |
               |  [Gemini 2.5 Flash Vision API]                   |
               |         └── Dynamic OCR & IMEI Verification     |
               |                                                 |
               |  [Firestore / BigQuery]                         |
               |         └── Real-time State & Audit Ledger      |
               +------------------------+------------------------+
                                        |
                                  Push Alerts / SMS
                                        |
                                        v
               +-------------------------------------------------+
               |             DEALER DASHBOARD UI                 |
               |                                                 |
               |  - Real-time Vault Status                       |
               |  - Instant OTP Authorization                    |
               |  - Automated IMEI & Inventory Accounting        |
               +-------------------------------------------------+

🧠 Gemini API Integration Details
VaultShield AI leverages Gemini 2.5 Flash for multi-modal computer vision processing inside the vault enclosure:
 * Sub-Second Optical Extraction: Inspects high-resolution snapshot images from inside the vault enclosure to extract printed packaging text and barcode data across varied lighting conditions and packaging materials.
 * Structured Data Schema: Enforces structured JSON output via response_mime_type="application/json" to bypass manual regex parsing.
 * Tamper & Anomaly Detection: Identifies unforced door openings, missing boxes, or obstructed camera lenses to flag security breaches immediately.
Structured Response Schema
{
  "slot_status": "OCCUPIED",
  "manufacturer": "Tecno",
  "model": "Spark 20 Pro",
  "storage_capacity": "256GB",
  "imei_number": "358912104928104",
  "box_condition": "INTACT",
  "confidence_score": 0.98
}

📁 Repository Structure
vaultshield-ai/
├── README.md                 # System Architecture & Documentation
├── LICENSE                   # MIT License
├── requirements.txt          # Global Python dependencies
├── hardware/
│   ├── vault_controller.py   # Raspberry Pi GPIO relay, sensors, & camera loop
│   └── config.py             # Edge hardware parameters
├── backend/
│   ├── main.py               # Cloud Run FastAPI application entry point
│   ├── gemini_service.py     # Gemini Vision API integration & prompt engine
│   ├── otp_manager.py        # TTL OTP generation & verification logic
│   └── Dockerfile            # Container configuration for Google Cloud Run
└── database/
    ├── firestore_schema.json # Document structure for real-time state sync
    └── bigquery_schema.sql   # SQL audit ledger tables for sales accounting

⚡ Getting Started
Prerequisites
 * Hardware: Raspberry Pi 3/4/Zero 2W, 12V Solenoid Lock, 5V Relay Module, USB or CSI Camera Module.
 * Software: Python 3.10+, Docker, Google Cloud SDK (gcloud).
 * API Keys: Google Gemini API Key, Firebase Service Account Credentials.
1. Cloud Backend Setup
 * Clone the repository:
   git clone [https://github.com/YOUR_USERNAME/vaultshield-ai.git](https://github.com/YOUR_USERNAME/vaultshield-ai.git)
cd vaultshield-ai/backend

 * Configure Environment Variables:
   Create a .env file inside the backend/ directory:
   GEMINI_API_KEY="your-gemini-api-key"
GCP_PROJECT_ID="your-gcp-project-id"
FIRESTORE_COLLECTION="vaults"
PORT=8080

 * Run Locally:
   pip install -r ../requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

 * Deploy to Google Cloud Run:
   gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/vaultshield-backend
gcloud run deploy vaultshield-backend \
  --image gcr.io/$GCP_PROJECT_ID/vaultshield-backend \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY

2. Edge Hardware Setup (Raspberry Pi)
 * Wire Hardware Relays:
   * Solenoid Relay Pin: GPIO 18
   * Door Sensor Switch: GPIO 23
   * Status LED: GPIO 24
 * Initialize Hardware Service:
   cd hardware
pip install -r requirements.txt
python vault_controller.py

📊 Database Schema (BigQuery Audit Ledger)
CREATE TABLE IF NOT EXISTS `vaultshield.sales_ledger` (
    transaction_id STRING NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    vault_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    manufacturer STRING,
    model STRING,
    imei STRING,
    retail_price NUMERIC,
    otp_verified BOOLEAN,
    gemini_ocr_raw JSON
);

📜 License
Distributed under the MIT License. See LICENSE for more information.

<FollowUp label="Want me to write the complete Dockerfile for deploying the backend to Cloud Run?" query="Write the complete Dockerfile and requirements.txt for deploying the VaultShield AI backend to Google Cloud Run."/>

