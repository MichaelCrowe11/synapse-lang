"""
Synapse-Lang Licensing System
Implements dual licensing model with feature flags
"""

import base64
import datetime
import hashlib
import json
import os
import platform
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class LicenseType(Enum):
    """License types available"""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ACADEMIC = "academic"
    TRIAL = "trial"

class FeatureFlag(Enum):
    """Feature flags for different editions"""
    # Core features (all editions)
    BASIC_INTERPRETER = "basic_interpreter"
    BASIC_PARALLEL = "basic_parallel"
    BASIC_UNCERTAIN = "basic_uncertain"
    BASIC_TENSOR = "basic_tensor"

    # Professional features
    ADVANCED_PARALLEL = "advanced_parallel"
    SYMBOLIC_ADVANCED = "symbolic_advanced"
    PIPELINE_ADVANCED = "pipeline_advanced"
    COMMERCIAL_USE = "commercial_use"

    # Enterprise features
    UNLIMITED_CORES = "unlimited_cores"
    GPU_ACCELERATION = "gpu_acceleration"
    QUANTUM_NET = "quantum_net"
    QUBIT_FLOW_UNLIMITED = "qubit_flow_unlimited"
    CLOUD_INTEGRATION = "cloud_integration"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_EXTENSIONS = "custom_extensions"
    TELEMETRY_ANALYTICS = "telemetry_analytics"

    # Academic features
    RESEARCH_TOOLS = "research_tools"
    EDUCATIONAL_MODE = "educational_mode"

@dataclass
class LicenseInfo:
    """License information"""
    license_key: str
    license_type: LicenseType
    owner: str
    organization: str | None
    email: str
    issued_date: datetime.datetime
    expiry_date: datetime.datetime | None
    max_cores: int
    max_qubits: int
    features: list[FeatureFlag]
    metadata: dict[str, Any]

class LicenseManager:
    """Manages licensing for Synapse-Lang"""

    # License validation server (would be your actual server)
    LICENSE_SERVER = "https://api.synapse-lang.com/v1/license"

    # Encryption key for local license storage (in production, use proper key management)
    MASTER_KEY = b"synapse-lang-2024-quantum-trinity-key-secret"

    # Feature sets for each license type
    FEATURE_SETS = {
        LicenseType.COMMUNITY: [
            FeatureFlag.BASIC_INTERPRETER,
            FeatureFlag.BASIC_PARALLEL,
            FeatureFlag.BASIC_UNCERTAIN,
            FeatureFlag.BASIC_TENSOR,
        ],
        LicenseType.PROFESSIONAL: [
            FeatureFlag.BASIC_INTERPRETER,
            FeatureFlag.BASIC_PARALLEL,
            FeatureFlag.BASIC_UNCERTAIN,
            FeatureFlag.BASIC_TENSOR,
            FeatureFlag.ADVANCED_PARALLEL,
            FeatureFlag.SYMBOLIC_ADVANCED,
            FeatureFlag.PIPELINE_ADVANCED,
            FeatureFlag.COMMERCIAL_USE,
        ],
        LicenseType.ENTERPRISE: [
            # All features
            FeatureFlag.BASIC_INTERPRETER,
            FeatureFlag.BASIC_PARALLEL,
            FeatureFlag.BASIC_UNCERTAIN,
            FeatureFlag.BASIC_TENSOR,
            FeatureFlag.ADVANCED_PARALLEL,
            FeatureFlag.SYMBOLIC_ADVANCED,
            FeatureFlag.PIPELINE_ADVANCED,
            FeatureFlag.COMMERCIAL_USE,
            FeatureFlag.UNLIMITED_CORES,
            FeatureFlag.GPU_ACCELERATION,
            FeatureFlag.QUANTUM_NET,
            FeatureFlag.QUBIT_FLOW_UNLIMITED,
            FeatureFlag.CLOUD_INTEGRATION,
            FeatureFlag.PRIORITY_SUPPORT,
            FeatureFlag.CUSTOM_EXTENSIONS,
            FeatureFlag.TELEMETRY_ANALYTICS,
        ],
        LicenseType.ACADEMIC: [
            FeatureFlag.BASIC_INTERPRETER,
            FeatureFlag.BASIC_PARALLEL,
            FeatureFlag.BASIC_UNCERTAIN,
            FeatureFlag.BASIC_TENSOR,
            FeatureFlag.ADVANCED_PARALLEL,
            FeatureFlag.SYMBOLIC_ADVANCED,
            FeatureFlag.PIPELINE_ADVANCED,
            FeatureFlag.RESEARCH_TOOLS,
            FeatureFlag.EDUCATIONAL_MODE,
            FeatureFlag.GPU_ACCELERATION,
        ],
        LicenseType.TRIAL: [
            # 30-day trial with most features
            FeatureFlag.BASIC_INTERPRETER,
            FeatureFlag.BASIC_PARALLEL,
            FeatureFlag.BASIC_UNCERTAIN,
            FeatureFlag.BASIC_TENSOR,
            FeatureFlag.ADVANCED_PARALLEL,
            FeatureFlag.SYMBOLIC_ADVANCED,
            FeatureFlag.PIPELINE_ADVANCED,
            FeatureFlag.GPU_ACCELERATION,
        ],
    }

    def __init__(self):
        self.current_license: LicenseInfo | None = None
        self.machine_id = self._get_machine_id()
        self.license_file = os.path.expanduser("~/.synapse-lang/license.json")
        self.cipher_suite = self._init_encryption()

        # Load existing license if available
        self.load_license()

    def _init_encryption(self) -> Fernet:
        """Initialize encryption for license storage"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"synapse-salt",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.MASTER_KEY))
        return Fernet(key)

    def _get_machine_id(self) -> str:
        """Get unique machine identifier"""
        # Combine multiple factors for machine ID
        factors = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            hex(uuid.getnode()),  # MAC address
        ]

        combined = "-".join(factors)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def validate_license_key(self, license_key: str) -> bool:
        """Validate a license key format"""
        # Format: XXXX-XXXX-XXXX-XXXX-XXXX
        parts = license_key.split("-")
        if len(parts) != 5:
            return False

        for part in parts:
            if len(part) != 4 or not part.isalnum():
                return False

        return True

    def activate_license(self, license_key: str, email: str) -> bool:
        """Activate a license key"""
        if not self.validate_license_key(license_key):
            raise ValueError("Invalid license key format")

        # In production, this would contact the license server
        # For demo, we'll create a mock license based on key pattern
        license_type = self._determine_license_type(license_key)

        self.current_license = LicenseInfo(
            license_key=license_key,
            license_type=license_type,
            owner="User",
            organization=None,
            email=email,
            issued_date=datetime.datetime.now(),
            expiry_date=self._calculate_expiry(license_type),
            max_cores=self._get_max_cores(license_type),
            max_qubits=self._get_max_qubits(license_type),
            features=self.FEATURE_SETS[license_type],
            metadata={
                "machine_id": self.machine_id,
                "activation_count": 1,
                "platform": platform.system(),
            }
        )

        self.save_license()
        return True

    def _determine_license_type(self, license_key: str) -> LicenseType:
        """Determine license type from key (mock implementation)"""
        # In production, this would be determined by the license server
        first_char = license_key[0].upper()

        if first_char in "ABC":
            return LicenseType.COMMUNITY
        elif first_char in "DEF":
            return LicenseType.PROFESSIONAL
        elif first_char in "GHI":
            return LicenseType.ENTERPRISE
        elif first_char in "JKL":
            return LicenseType.ACADEMIC
        else:
            return LicenseType.TRIAL

    def _calculate_expiry(self, license_type: LicenseType) -> datetime.datetime | None:
        """Calculate license expiry date"""
        if license_type == LicenseType.TRIAL:
            return datetime.datetime.now() + datetime.timedelta(days=30)
        elif license_type in [LicenseType.PROFESSIONAL, LicenseType.ACADEMIC]:
            return datetime.datetime.now() + datetime.timedelta(days=365)
        elif license_type == LicenseType.ENTERPRISE:
            return None  # Perpetual
        else:
            return None  # Community is perpetual

    def _get_max_cores(self, license_type: LicenseType) -> int:
        """Get maximum cores for license type"""
        limits = {
            LicenseType.COMMUNITY: 4,
            LicenseType.PROFESSIONAL: 16,
            LicenseType.ENTERPRISE: -1,  # Unlimited
            LicenseType.ACADEMIC: 32,
            LicenseType.TRIAL: 8,
        }
        return limits.get(license_type, 4)

    def _get_max_qubits(self, license_type: LicenseType) -> int:
        """Get maximum qubits for license type"""
        limits = {
            LicenseType.COMMUNITY: 30,
            LicenseType.PROFESSIONAL: 100,
            LicenseType.ENTERPRISE: -1,  # Unlimited
            LicenseType.ACADEMIC: 200,
            LicenseType.TRIAL: 50,
        }
        return limits.get(license_type, 30)

    def save_license(self):
        """Save license to encrypted file"""
        if not self.current_license:
            return

        # Create directory if needed
        os.makedirs(os.path.dirname(self.license_file), exist_ok=True)

        # Serialize license
        license_data = {
            "license_key": self.current_license.license_key,
            "license_type": self.current_license.license_type.value,
            "owner": self.current_license.owner,
            "organization": self.current_license.organization,
            "email": self.current_license.email,
            "issued_date": self.current_license.issued_date.isoformat(),
            "expiry_date": self.current_license.expiry_date.isoformat() if self.current_license.expiry_date else None,
            "max_cores": self.current_license.max_cores,
            "max_qubits": self.current_license.max_qubits,
            "features": [f.value for f in self.current_license.features],
            "metadata": self.current_license.metadata,
        }

        # Encrypt and save
        encrypted_data = self.cipher_suite.encrypt(json.dumps(license_data).encode())

        with open(self.license_file, "wb") as f:
            f.write(encrypted_data)

    def load_license(self) -> bool:
        """Load license from encrypted file"""
        if not os.path.exists(self.license_file):
            # Default to community edition
            self.current_license = self._get_community_license()
            return False

        try:
            with open(self.license_file, "rb") as f:
                encrypted_data = f.read()

            # Decrypt
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data)

            # Reconstruct license
            self.current_license = LicenseInfo(
                license_key=license_data["license_key"],
                license_type=LicenseType(license_data["license_type"]),
                owner=license_data["owner"],
                organization=license_data["organization"],
                email=license_data["email"],
                issued_date=datetime.datetime.fromisoformat(license_data["issued_date"]),
                expiry_date=datetime.datetime.fromisoformat(license_data["expiry_date"]) if license_data["expiry_date"] else None,
                max_cores=license_data["max_cores"],
                max_qubits=license_data["max_qubits"],
                features=[FeatureFlag(f) for f in license_data["features"]],
                metadata=license_data["metadata"],
            )

            # Validate expiry
            if self.current_license.expiry_date and datetime.datetime.now() > self.current_license.expiry_date:
                print("WARNING: License has expired. Reverting to Community Edition.")
                self.current_license = self._get_community_license()
                return False

            return True

        except Exception as e:
            print(f"Error loading license: {e}")
            self.current_license = self._get_community_license()
            return False

    def _get_community_license(self) -> LicenseInfo:
        """Get default community license"""
        return LicenseInfo(
            license_key="COMM-UNIT-Y000-FREE-0000",
            license_type=LicenseType.COMMUNITY,
            owner="Community User",
            organization=None,
            email="user@community",
            issued_date=datetime.datetime.now(),
            expiry_date=None,
            max_cores=4,
            max_qubits=30,
            features=self.FEATURE_SETS[LicenseType.COMMUNITY],
            metadata={"machine_id": self.machine_id},
        )

    def has_feature(self, feature: FeatureFlag) -> bool:
        """Check if current license has a feature"""
        if not self.current_license:
            return feature in self.FEATURE_SETS[LicenseType.COMMUNITY]

        return feature in self.current_license.features

    def check_limits(self, cores: int | None = None, qubits: int | None = None) -> bool:
        """Check if operation is within license limits"""
        if not self.current_license:
            return False

        if cores and self.current_license.max_cores != -1:
            if cores > self.current_license.max_cores:
                raise LicenseError(f"License limited to {self.current_license.max_cores} cores, requested {cores}")

        if qubits and self.current_license.max_qubits != -1:
            if qubits > self.current_license.max_qubits:
                raise LicenseError(f"License limited to {self.current_license.max_qubits} qubits, requested {qubits}")

        return True

    def get_license_info(self) -> dict[str, Any]:
        """Get current license information"""
        if not self.current_license:
            self.current_license = self._get_community_license()

        return {
            "type": self.current_license.license_type.value,
            "owner": self.current_license.owner,
            "organization": self.current_license.organization,
            "email": self.current_license.email,
            "issued": self.current_license.issued_date.isoformat(),
            "expires": self.current_license.expiry_date.isoformat() if self.current_license.expiry_date else "Never",
            "max_cores": "Unlimited" if self.current_license.max_cores == -1 else self.current_license.max_cores,
            "max_qubits": "Unlimited" if self.current_license.max_qubits == -1 else self.current_license.max_qubits,
            "features": [f.value for f in self.current_license.features],
        }

    def generate_license_key(self, license_type: LicenseType, seed: str | None = None) -> str:
        """Generate a license key (for testing/demo)"""
        import random
        import string

        if seed:
            random.seed(seed)

        # Determine prefix based on type
        prefixes = {
            LicenseType.COMMUNITY: "C",
            LicenseType.PROFESSIONAL: "P",
            LicenseType.ENTERPRISE: "E",
            LicenseType.ACADEMIC: "A",
            LicenseType.TRIAL: "T",
        }

        prefix = prefixes.get(license_type, "X")

        # Generate key parts
        parts = []
        for i in range(5):
            if i == 0:
                # First part starts with type identifier
                part = prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
            else:
                part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            parts.append(part)

        return "-".join(parts)

class LicenseError(Exception):
    """License-related errors"""
    pass

# Global license manager instance
_license_manager = None

def get_license_manager() -> LicenseManager:
    """Get global license manager instance"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager

def require_feature(feature: FeatureFlag):
    """Decorator to require a feature flag"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            lm = get_license_manager()
            if not lm.has_feature(feature):
                raise LicenseError(f"Feature '{feature.value}' requires a higher license tier")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_license_limits(cores: int | None = None, qubits: int | None = None):
    """Decorator to check license limits"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            lm = get_license_manager()
            lm.check_limits(cores=cores, qubits=qubits)
            return func(*args, **kwargs)
        return wrapper
    return decorator
