import secrets
import time
from typing import Dict, Optional

class OTPManager:
    """Handles time-to-live (TTL) single-use OTP generation and verification."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        # In-memory store; production maps to Redis or Firestore
        self._otp_store: Dict[str, dict] = {}

    def generate_otp(self, vault_id: str, agent_id: str) -> str:
        """Generates a secure 6-digit OTP valid for the specified TTL."""
        otp = f"{secrets.randbelow(1000000):06d}"
        self._otp_store[otp] = {
            "vault_id": vault_id,
            "agent_id": agent_id,
            "expires_at": time.time() + self.ttl_seconds
        }
        return otp

    def verify_and_consume_otp(self, otp: str, vault_id: str) -> Optional[dict]:
        """Validates OTP against vault ID and consumes it upon first use."""
        record = self._otp_store.get(otp)
        
        if not record:
            return None
            
        if record["vault_id"] != vault_id or time.time() > record["expires_at"]:
            del self._otp_store[otp]  # Clean expired or invalid record
            return None

        # Single-use consumption
        del self._otp_store[otp]
        return record

otp_manager = OTPManager()
