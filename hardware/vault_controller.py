import time
import requests
import cv2

# Hardware Configurations
CLOUD_RUN_ENDPOINT = "https://your-cloud-run-url.run.app/api/v1/verify-and-audit"
VAULT_ID = "VAULT_KADUNA_01"

# Raspberry Pi GPIO Pins (Mocked for testing environments)
SOLENOID_RELAY_PIN = 18
DOOR_SENSOR_PIN = 23

def set_gpio_pin(pin, state):
    """Simulates/Triggers GPIO pin state change for solenoid relay."""
    # Example using RPi.GPIO:
    # import RPi.GPIO as GPIO
    # GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
    print(f"[GPIO Action] Pin {pin} set to {'HIGH (UNLOCKED)' if state else 'LOW (LOCKED)'}")

def capture_interior_snapshot():
    """Captures an image frame from the vault webcam."""
    print("[Camera] Initializing web camera frame capture...")
    cap = cv2.VideoCapture(0)
    
    # Allow camera time to warm up / auto-exposure adjustment
    time.sleep(1)
    ret, frame = cap.read()
    cap.release()

    if ret:
        _, img_encoded = cv2.imencode('.jpg', frame)
        print("[Camera] Frame capture successful.")
        return img_encoded.tobytes()
    else:
        print("[Camera Error] Failed to read frame from webcam!")
        return None

def process_dispatch_request(otp_input: str):
    """Sends OTP and internal snapshot to Cloud Run backend."""
    image_data = capture_interior_snapshot()
    if not image_data:
        print("Aborting: Camera feed unavailable.")
        return False

    print(f"[Network] Transmitting OTP '{otp_input}' and snapshot to Cloud Run...")
    files = {"file": ("snapshot.jpg", image_data, "image/jpeg")}
    data = {"vault_id": VAULT_ID, "otp": otp_input}

    try:
        response = requests.post(CLOUD_RUN_ENDPOINT, data=data, files=files, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ [SUCCESS] Dealer Authorized Dispatch!")
            print(f"📦 Extracted Device: {result.get('extracted_device')}")
            
            # Unlock Solenoid for 10 Seconds
            set_gpio_pin(SOLENOID_RELAY_PIN, True)
            time.sleep(10)
            set_gpio_pin(SOLENOID_RELAY_PIN, False)
            print("[Hardware] Solenoid re-engaged. Door locked.")
            return True
        else:
            print(f"❌ [REJECTED] {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ [Network Failure] {str(e)}")
        return False

if __name__ == "__main__":
    print("=== VaultShield AI Edge Controller Started ===")
    user_otp = input("Enter 6-digit Dealer OTP to request vault unlock: ").strip()
    process_dispatch_request(user_otp)
