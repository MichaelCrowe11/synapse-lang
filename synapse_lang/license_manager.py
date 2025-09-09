"""
Synapse Language - License Management System
Handles license validation, feature gating, and telemetry
"""

import os
import json
import time
import hashlib
import platform
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import requests

class LicenseType:
    EVALUATION = "evaluation"
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ACADEMIC = "academic"
    COMMUNITY = "community"

class Features:
    """Feature flags for different license tiers"""
    
    # Community/Evaluation limits
    MAX_CORES_COMMUNITY = 4
    MAX_TENSOR_SIZE_COMMUNITY = 1000
    MAX_PARALLEL_BRANCHES_COMMUNITY = 2
    
    # Professional limits
    MAX_CORES_PROFESSIONAL = 16
    MAX_TENSOR_SIZE_PROFESSIONAL = 100000
    
    # Enterprise = unlimited

class LicenseManager:
    """Manages license validation and feature access"""
    
    LICENSE_SERVER = "https://api.synapse-lang.com/v1/license"
    TELEMETRY_SERVER = "https://telemetry.synapse-lang.com/v1/events"
    
    def __init__(self):
        self.license_file = Path.home() / ".synapse" / "license.key"
        self.telemetry_file = Path.home() / ".synapse" / "telemetry.json"
        self.license_data = None
        self.features = {}
        self.telemetry_queue = []
        self.machine_id = self._get_machine_id()
        
        # Ensure directories exist
        self.license_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load and validate license
        self._load_license()
        self._start_telemetry_thread()
    
    def _get_machine_id(self) -> str:
        """Generate unique machine identifier"""
        info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
        return hashlib.sha256(info.encode()).hexdigest()[:16]
    
    def _load_license(self):
        """Load license from file or use community edition"""
        if self.license_file.exists():
            try:
                with open(self.license_file, 'r') as f:
                    key = f.read().strip()
                    self.validate_license(key)
            except Exception:
                self._set_community_license()
        else:
            self._set_community_license()
    
    def _set_community_license(self):
        """Set community edition limits"""
        self.license_data = {
            "type": LicenseType.COMMUNITY,
            "expires": None,
            "features": {
                "max_cores": Features.MAX_CORES_COMMUNITY,
                "max_tensor_size": Features.MAX_TENSOR_SIZE_COMMUNITY,
                "max_parallel_branches": Features.MAX_PARALLEL_BRANCHES_COMMUNITY,
                "gpu_enabled": False,
                "quantum_enabled": False,
                "jit_enabled": True,
                "telemetry_required": True,
                "watermark": True,
            }
        }
        self._apply_features()
    
    def validate_license(self, license_key: str) -> bool:
        """Validate license key and set features"""
        try:
            # Decode license key
            decoded = self._decode_license_key(license_key)
            
            # Check expiration
            if decoded.get("expires"):
                expiry = datetime.fromisoformat(decoded["expires"])
                if expiry < datetime.now():
                    print("⚠️  License expired. Reverting to Community Edition.")
                    self._set_community_license()
                    return False
            
            # Check machine binding
            if decoded.get("machine_id") and decoded["machine_id"] != self.machine_id:
                print("⚠️  License not valid for this machine.")
                self._set_community_license()
                return False
            
            # Apply license
            self.license_data = decoded
            self._apply_features()
            
            # Save license
            with open(self.license_file, 'w') as f:
                f.write(license_key)
            
            # Verify with server (async)
            threading.Thread(target=self._verify_online, args=(license_key,)).start()
            
            return True
            
        except Exception as e:
            print(f"⚠️  Invalid license: {e}")
            self._set_community_license()
            return False
    
    def _decode_license_key(self, key: str) -> Dict:
        """Decode and verify license key signature"""
        try:
            # Simple decode for demo - in production use proper cryptography
            parts = key.split('-')
            if len(parts) != 5:
                raise ValueError("Invalid license format")
            
            # Extract license data
            license_type = parts[0]
            expires = parts[1]
            features = parts[2]
            machine = parts[3]
            signature = parts[4]
            
            # Verify signature (simplified)
            expected_sig = hashlib.sha256(f"{license_type}{expires}{features}{machine}".encode()).hexdigest()[:8]
            if signature != expected_sig:
                raise ValueError("Invalid license signature")
            
            # Parse license data
            return {
                "type": license_type,
                "expires": datetime.fromtimestamp(int(expires)) if expires != "0" else None,
                "machine_id": machine if machine != "ANY" else None,
                "features": self._get_features_for_type(license_type)
            }
        except Exception:
            raise ValueError("Invalid license key")
    
    def _get_features_for_type(self, license_type: str) -> Dict:
        """Get feature set for license type"""
        features = {
            LicenseType.EVALUATION: {
                "max_cores": 2,
                "max_tensor_size": 100,
                "max_parallel_branches": 1,
                "gpu_enabled": False,
                "quantum_enabled": False,
                "jit_enabled": False,
                "telemetry_required": True,
                "watermark": True,
                "trial_days": 30,
            },
            LicenseType.PERSONAL: {
                "max_cores": 8,
                "max_tensor_size": 10000,
                "max_parallel_branches": 4,
                "gpu_enabled": False,
                "quantum_enabled": False,
                "jit_enabled": True,
                "telemetry_required": True,
                "watermark": False,
            },
            LicenseType.PROFESSIONAL: {
                "max_cores": 16,
                "max_tensor_size": 100000,
                "max_parallel_branches": 8,
                "gpu_enabled": True,
                "quantum_enabled": False,
                "jit_enabled": True,
                "telemetry_required": True,
                "watermark": False,
            },
            LicenseType.ENTERPRISE: {
                "max_cores": -1,  # Unlimited
                "max_tensor_size": -1,
                "max_parallel_branches": -1,
                "gpu_enabled": True,
                "quantum_enabled": True,
                "jit_enabled": True,
                "telemetry_required": False,
                "watermark": False,
            },
            LicenseType.ACADEMIC: {
                "max_cores": 16,
                "max_tensor_size": 100000,
                "max_parallel_branches": 8,
                "gpu_enabled": True,
                "quantum_enabled": True,
                "jit_enabled": True,
                "telemetry_required": True,
                "watermark": False,
                "require_edu_email": True,
            },
        }
        return features.get(license_type, features[LicenseType.COMMUNITY])
    
    def _apply_features(self):
        """Apply license features to runtime"""
        if self.license_data:
            self.features = self.license_data.get("features", {})
            
            # Apply limits
            if self.features.get("max_cores", -1) > 0:
                os.environ["SYNAPSE_MAX_CORES"] = str(self.features["max_cores"])
            
            if not self.features.get("gpu_enabled"):
                os.environ["SYNAPSE_DISABLE_GPU"] = "1"
            
            if not self.features.get("quantum_enabled"):
                os.environ["SYNAPSE_DISABLE_QUANTUM"] = "1"
    
    def check_feature(self, feature: str) -> bool:
        """Check if feature is available in current license"""
        return self.features.get(feature, False)
    
    def check_limit(self, limit: str, value: int) -> bool:
        """Check if value is within license limits"""
        max_value = self.features.get(limit, 0)
        if max_value == -1:  # Unlimited
            return True
        return value <= max_value
    
    def add_watermark(self, output: str) -> str:
        """Add watermark to output if required"""
        if self.features.get("watermark"):
            return f"{output}\n[Generated with Synapse Community Edition - https://synapse-lang.com]"
        return output
    
    def _verify_online(self, license_key: str):
        """Verify license with online server"""
        try:
            response = requests.post(
                self.LICENSE_SERVER + "/verify",
                json={
                    "key": license_key,
                    "machine_id": self.machine_id,
                    "version": "1.0.0"
                },
                timeout=5
            )
            if response.status_code != 200:
                print("⚠️  Online license verification failed")
        except Exception:
            pass  # Offline mode allowed
    
    def track_usage(self, event: str, data: Optional[Dict] = None):
        """Track usage telemetry"""
        if not self.features.get("telemetry_required", True):
            return
        
        telemetry_event = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "license_type": self.license_data.get("type"),
            "machine_id": self.machine_id,
            "data": data or {}
        }
        
        self.telemetry_queue.append(telemetry_event)
    
    def _start_telemetry_thread(self):
        """Start background thread for telemetry"""
        def send_telemetry():
            while True:
                time.sleep(60)  # Send every minute
                if self.telemetry_queue:
                    try:
                        requests.post(
                            self.TELEMETRY_SERVER,
                            json={"events": self.telemetry_queue[:100]},  # Batch send
                            timeout=5
                        )
                        self.telemetry_queue = self.telemetry_queue[100:]
                    except Exception:
                        pass  # Ignore telemetry failures
        
        thread = threading.Thread(target=send_telemetry, daemon=True)
        thread.start()
    
    def generate_trial_license(self) -> str:
        """Generate a 30-day trial license"""
        expires = int((datetime.now() + timedelta(days=30)).timestamp())
        key_parts = [
            LicenseType.EVALUATION,
            str(expires),
            "TRIAL",
            self.machine_id,
        ]
        signature = hashlib.sha256("".join(key_parts).encode()).hexdigest()[:8]
        key_parts.append(signature)
        return "-".join(key_parts)
    
    def get_license_info(self) -> Dict:
        """Get current license information"""
        return {
            "type": self.license_data.get("type", "community"),
            "expires": self.license_data.get("expires"),
            "features": self.features,
            "machine_id": self.machine_id
        }

# Global license manager instance
_license_manager = None

def get_license_manager() -> LicenseManager:
    """Get global license manager instance"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager

def check_license_feature(feature: str) -> bool:
    """Check if feature is available"""
    return get_license_manager().check_feature(feature)

def check_license_limit(limit: str, value: int) -> bool:
    """Check if value is within limits"""
    return get_license_manager().check_limit(limit, value)

def track_usage(event: str, data: Optional[Dict] = None):
    """Track usage telemetry"""
    get_license_manager().track_usage(event, data)