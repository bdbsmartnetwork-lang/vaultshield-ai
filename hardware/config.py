import os

# Hardware GPIO Pin Mappings (Raspberry Pi BCM standard)
SOLENOID_RELAY_PIN = 18    # Relay trigger for 12V solenoid lock
DOOR_SENSOR_PIN = 23       # Magnetic reed switch for door open/close
ALARM_SIREN_PIN = 24       # Onboard buzzer/siren trigger
STATUS_LED_GREEN = 25      # Authorization indicator
STATUS_LED_RED = 8         # Breach / Error indicator

# Operational Parameters
SOLENOID_UNLOCK_DURATION = 10  # Seconds door stays unlocked after OTP match
CAMERA_DEVICE_INDEX = 0        # Default USB/CSI video camera index
CAMERA_WARMUP_TIME = 1.5       # Camera auto-exposure buffer in seconds

# Network Settings
VAULT_ID = os.getenv("VAULT_ID", "VAULT_KADUNA_01")
CLOUD_RUN_ENDPOINT = os.getenv(
    "CLOUD_RUN_ENDPOINT", 
    "https://vaultshield-backend-uc.a.run.app/api/v1/verify-and-audit"
)
