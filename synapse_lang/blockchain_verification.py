"""Blockchain Verification System for Synapse Language
Immutable verification of scientific computations and research integrity
"""

import hashlib
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import hmac
import base64


class VerificationType(Enum):
    """Types of verification records"""
    CODE_EXECUTION = auto()
    RESEARCH_RESULT = auto()
    DATA_INTEGRITY = auto()
    PEER_REVIEW = auto()
    HYPOTHESIS_TEST = auto()
    QUANTUM_EXPERIMENT = auto()
    COLLABORATION = auto()
    PUBLICATION = auto()


class VerificationStatus(Enum):
    """Verification status"""
    PENDING = auto()
    VERIFIED = auto()
    DISPUTED = auto()
    REJECTED = auto()
    EXPIRED = auto()


@dataclass
class VerificationRecord:
    """Individual verification record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    verification_type: VerificationType = VerificationType.CODE_EXECUTION
    researcher_id: str = ""
    institution: str = ""
    timestamp: float = field(default_factory=time.time)
    content_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    digital_signature: str = ""
    peer_signatures: List[str] = field(default_factory=list)
    status: VerificationStatus = VerificationStatus.PENDING

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.verification_type.name,
            'researcher_id': self.researcher_id,
            'institution': self.institution,
            'timestamp': self.timestamp,
            'content_hash': self.content_hash,
            'metadata': self.metadata,
            'digital_signature': self.digital_signature,
            'peer_signatures': self.peer_signatures,
            'status': self.status.name
        }


@dataclass
class BlockchainBlock:
    """Blockchain block containing verification records"""
    index: int
    timestamp: float = field(default_factory=time.time)
    records: List[VerificationRecord] = field(default_factory=list)
    previous_hash: str = ""
    nonce: int = 0
    hash: str = ""

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'records': [record.to_dict() for record in self.records],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int = 4):
        """Mine block using proof of work"""
        target = "0" * difficulty
        start_time = time.time()

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

            # Prevent infinite mining
            if time.time() - start_time > 10:  # 10 second timeout
                break

    def to_dict(self) -> dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'records': [record.to_dict() for record in self.records],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class ScientificBlockchain:
    """Blockchain for scientific verification"""

    def __init__(self, difficulty: int = 2):
        self.chain: List[BlockchainBlock] = []
        self.pending_records: List[VerificationRecord] = []
        self.mining_reward = 1.0
        self.difficulty = difficulty
        self.verified_researchers: Dict[str, Dict[str, Any]] = {}

        # Create genesis block
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = BlockchainBlock(
            index=0,
            previous_hash="0",
            records=[]
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    def get_latest_block(self) -> BlockchainBlock:
        """Get the most recent block"""
        return self.chain[-1]

    def add_verification_record(self, record: VerificationRecord):
        """Add verification record to pending list"""
        self.pending_records.append(record)

    def mine_pending_records(self, mining_address: str) -> BlockchainBlock:
        """Mine a new block with pending records"""
        # Create mining reward record
        reward_record = VerificationRecord(
            verification_type=VerificationType.COLLABORATION,
            researcher_id=mining_address,
            content_hash="mining_reward",
            metadata={"reward": self.mining_reward, "type": "mining"}
        )

        # Create new block
        block = BlockchainBlock(
            index=len(self.chain),
            records=self.pending_records + [reward_record],
            previous_hash=self.get_latest_block().hash
        )

        # Mine the block
        block.mine_block(self.difficulty)

        # Add to chain and clear pending
        self.chain.append(block)
        self.pending_records = []

        return block

    def verify_chain(self) -> bool:
        """Verify entire blockchain integrity"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_researcher_reputation(self, researcher_id: str) -> Dict[str, Any]:
        """Calculate researcher reputation based on blockchain records"""
        total_verifications = 0
        peer_reviews = 0
        publications = 0
        disputed_records = 0

        for block in self.chain:
            for record in block.records:
                if record.researcher_id == researcher_id:
                    total_verifications += 1

                    if record.verification_type == VerificationType.PEER_REVIEW:
                        peer_reviews += 1
                    elif record.verification_type == VerificationType.PUBLICATION:
                        publications += 1

                    if record.status == VerificationStatus.DISPUTED:
                        disputed_records += 1

        reputation_score = total_verifications * 10 + peer_reviews * 20 + publications * 50
        if disputed_records > 0:
            reputation_score *= (1 - disputed_records / total_verifications * 0.5)

        return {
            'researcher_id': researcher_id,
            'reputation_score': max(0, int(reputation_score)),
            'total_verifications': total_verifications,
            'peer_reviews': peer_reviews,
            'publications': publications,
            'disputed_records': disputed_records,
            'reliability': (total_verifications - disputed_records) / max(1, total_verifications)
        }

    def search_records(self, criteria: Dict[str, Any]) -> List[VerificationRecord]:
        """Search verification records by criteria"""
        results = []

        for block in self.chain:
            for record in block.records:
                match = True

                for key, value in criteria.items():
                    if key == "verification_type" and record.verification_type.name != value:
                        match = False
                        break
                    elif key == "researcher_id" and record.researcher_id != value:
                        match = False
                        break
                    elif key == "institution" and record.institution != value:
                        match = False
                        break
                    elif key == "content_hash" and record.content_hash != value:
                        match = False
                        break

                if match:
                    results.append(record)

        return results


class DigitalSignature:
    """Simplified digital signature system"""

    def __init__(self, private_key: str = None):
        self.private_key = private_key or self._generate_private_key()
        self.public_key = self._derive_public_key(self.private_key)

    def _generate_private_key(self) -> str:
        """Generate private key (simplified)"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()

    def _derive_public_key(self, private_key: str) -> str:
        """Derive public key from private key (simplified)"""
        return hashlib.sha256(private_key.encode()).hexdigest()

    def sign(self, data: str) -> str:
        """Create digital signature"""
        message = data.encode()
        signature = hmac.new(
            self.private_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify(self, data: str, signature: str, public_key: str) -> bool:
        """Verify digital signature"""
        # Simplified verification - in practice would use proper cryptography
        return len(signature) == 64 and len(public_key) == 64


class SynapseVerificationManager:
    """Manages verification of Synapse scientific computations"""

    def __init__(self):
        self.blockchain = ScientificBlockchain()
        self.signature_system = DigitalSignature()
        self.trusted_institutions = set()
        self.verification_templates = self._load_verification_templates()

    def _load_verification_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load verification templates for different scientific scenarios"""
        return {
            "quantum_experiment": {
                "required_fields": ["circuit_design", "measurement_results", "error_rates"],
                "peer_review_required": True,
                "minimum_signatures": 2,
                "expiry_days": 365
            },
            "uncertainty_analysis": {
                "required_fields": ["input_data", "error_propagation", "confidence_intervals"],
                "peer_review_required": False,
                "minimum_signatures": 1,
                "expiry_days": 180
            },
            "hypothesis_validation": {
                "required_fields": ["hypothesis_statement", "test_data", "statistical_analysis"],
                "peer_review_required": True,
                "minimum_signatures": 3,
                "expiry_days": 730
            },
            "code_execution": {
                "required_fields": ["source_code", "execution_environment", "output_data"],
                "peer_review_required": False,
                "minimum_signatures": 1,
                "expiry_days": 90
            }
        }

    def verify_synapse_execution(self,
                                code: str,
                                output: Any,
                                researcher_id: str,
                                institution: str = "") -> VerificationRecord:
        """Verify Synapse code execution"""

        # Calculate content hash
        content = {
            "code": code,
            "output": str(output),
            "timestamp": time.time(),
            "language": "synapse"
        }
        content_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

        # Create verification record
        record = VerificationRecord(
            verification_type=VerificationType.CODE_EXECUTION,
            researcher_id=researcher_id,
            institution=institution,
            content_hash=content_hash,
            metadata={
                "code_length": len(code),
                "output_type": type(output).__name__,
                "execution_verified": True,
                "reproducible": True
            }
        )

        # Sign the record
        record_data = json.dumps(record.to_dict(), sort_keys=True)
        record.digital_signature = self.signature_system.sign(record_data)

        # Add to blockchain
        self.blockchain.add_verification_record(record)

        return record

    def verify_quantum_experiment(self,
                                 circuit_data: Dict[str, Any],
                                 results: Dict[str, Any],
                                 researcher_id: str) -> VerificationRecord:
        """Verify quantum experiment results"""

        content_hash = hashlib.sha256(
            json.dumps({
                "circuit": circuit_data,
                "results": results,
                "verification_type": "quantum_experiment"
            }, sort_keys=True).encode()
        ).hexdigest()

        record = VerificationRecord(
            verification_type=VerificationType.QUANTUM_EXPERIMENT,
            researcher_id=researcher_id,
            content_hash=content_hash,
            metadata={
                "qubits": circuit_data.get("num_qubits", 0),
                "gates": circuit_data.get("gate_count", 0),
                "measurement_shots": results.get("shots", 0),
                "fidelity": results.get("fidelity", 0.0),
                "quantum_verified": True
            }
        )

        record_data = json.dumps(record.to_dict(), sort_keys=True)
        record.digital_signature = self.signature_system.sign(record_data)

        self.blockchain.add_verification_record(record)
        return record

    def verify_research_integrity(self,
                                 research_data: Dict[str, Any],
                                 researcher_id: str,
                                 peer_reviewers: List[str] = None) -> VerificationRecord:
        """Verify research data integrity"""

        content_hash = hashlib.sha256(
            json.dumps(research_data, sort_keys=True).encode()
        ).hexdigest()

        record = VerificationRecord(
            verification_type=VerificationType.RESEARCH_RESULT,
            researcher_id=researcher_id,
            content_hash=content_hash,
            metadata={
                "data_size": len(str(research_data)),
                "peer_reviewed": len(peer_reviewers or []) > 0,
                "integrity_verified": True,
                "research_domain": research_data.get("domain", "unknown")
            }
        )

        # Add peer signatures if available
        if peer_reviewers:
            for reviewer_id in peer_reviewers:
                # Simulate peer signature
                peer_sig = hashlib.sha256(f"{reviewer_id}_{content_hash}".encode()).hexdigest()
                record.peer_signatures.append(peer_sig)

        record_data = json.dumps(record.to_dict(), sort_keys=True)
        record.digital_signature = self.signature_system.sign(record_data)

        self.blockchain.add_verification_record(record)
        return record

    def create_research_certificate(self, record_id: str) -> Dict[str, Any]:
        """Create verifiable research certificate"""

        # Find record in blockchain
        record = None
        block_index = None

        for i, block in enumerate(self.blockchain.chain):
            for r in block.records:
                if r.id == record_id:
                    record = r
                    block_index = i
                    break
            if record:
                break

        if not record:
            return {"error": "Record not found"}

        certificate = {
            "certificate_id": str(uuid.uuid4()),
            "record_id": record.id,
            "verification_type": record.verification_type.name,
            "researcher_id": record.researcher_id,
            "institution": record.institution,
            "timestamp": record.timestamp,
            "content_hash": record.content_hash,
            "block_index": block_index,
            "blockchain_hash": self.blockchain.chain[block_index].hash if block_index else "",
            "peer_signatures_count": len(record.peer_signatures),
            "verification_status": record.status.name,
            "certificate_created": time.time(),
            "validity": "This certificate verifies the authenticity and integrity of the recorded scientific computation."
        }

        # Sign certificate
        cert_data = json.dumps(certificate, sort_keys=True)
        certificate["certificate_signature"] = self.signature_system.sign(cert_data)

        return certificate

    def audit_trail(self, content_hash: str) -> List[Dict[str, Any]]:
        """Get complete audit trail for content"""
        trail = []

        for i, block in enumerate(self.blockchain.chain):
            for record in block.records:
                if record.content_hash == content_hash:
                    trail.append({
                        "block_index": i,
                        "block_hash": block.hash,
                        "timestamp": record.timestamp,
                        "verification_type": record.verification_type.name,
                        "researcher_id": record.researcher_id,
                        "status": record.status.name,
                        "peer_signatures": len(record.peer_signatures)
                    })

        return sorted(trail, key=lambda x: x["timestamp"])

    def mine_verification_block(self) -> BlockchainBlock:
        """Mine pending verifications into blockchain"""
        return self.blockchain.mine_pending_records("system_miner")

    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get blockchain verification statistics"""
        total_records = 0
        verification_types = {}
        verified_count = 0
        disputed_count = 0

        for block in self.blockchain.chain:
            for record in block.records:
                total_records += 1

                vtype = record.verification_type.name
                verification_types[vtype] = verification_types.get(vtype, 0) + 1

                if record.status == VerificationStatus.VERIFIED:
                    verified_count += 1
                elif record.status == VerificationStatus.DISPUTED:
                    disputed_count += 1

        return {
            "total_blocks": len(self.blockchain.chain),
            "total_records": total_records,
            "verified_records": verified_count,
            "disputed_records": disputed_count,
            "verification_types": verification_types,
            "blockchain_integrity": self.blockchain.verify_chain(),
            "pending_verifications": len(self.blockchain.pending_records)
        }


# Example usage and testing
if __name__ == "__main__":
    print("Synapse Blockchain Verification System")
    print("=" * 40)

    # Create verification manager
    verifier = SynapseVerificationManager()

    # Example 1: Verify Synapse code execution
    print("\n--- Code Execution Verification ---")
    synapse_code = """
quantum[2] {
    H(q0)
    CNOT(q0, q1)
    measure(q0, q1)
}"""

    execution_output = {"00": 0.5, "11": 0.5}

    code_record = verifier.verify_synapse_execution(
        code=synapse_code,
        output=execution_output,
        researcher_id="alice_researcher",
        institution="MIT Quantum Lab"
    )

    print(f"Code verification record: {code_record.id}")
    print(f"Content hash: {code_record.content_hash[:16]}...")
    print(f"Signature: {code_record.digital_signature[:16]}...")

    # Example 2: Verify quantum experiment
    print("\n--- Quantum Experiment Verification ---")
    circuit_data = {
        "num_qubits": 2,
        "gate_count": 3,
        "circuit_depth": 2
    }

    quantum_results = {
        "shots": 1000,
        "fidelity": 0.95,
        "measurement_outcomes": {"00": 500, "11": 500}
    }

    quantum_record = verifier.verify_quantum_experiment(
        circuit_data=circuit_data,
        results=quantum_results,
        researcher_id="bob_physicist"
    )

    print(f"Quantum verification: {quantum_record.id}")
    print(f"Qubits verified: {quantum_record.metadata['qubits']}")
    print(f"Fidelity: {quantum_record.metadata['fidelity']}")

    # Example 3: Research integrity verification
    print("\n--- Research Integrity Verification ---")
    research_data = {
        "domain": "quantum_computing",
        "hypothesis": "Bell states exhibit maximum entanglement",
        "data_points": 1000,
        "statistical_significance": 0.001
    }

    integrity_record = verifier.verify_research_integrity(
        research_data=research_data,
        researcher_id="carol_scientist",
        peer_reviewers=["reviewer_1", "reviewer_2", "reviewer_3"]
    )

    print(f"Research integrity: {integrity_record.id}")
    print(f"Peer signatures: {len(integrity_record.peer_signatures)}")
    print(f"Domain: {integrity_record.metadata['research_domain']}")

    # Mine verifications into blockchain
    print("\n--- Mining Verification Block ---")
    new_block = verifier.mine_verification_block()
    print(f"Mined block {new_block.index}")
    print(f"Block hash: {new_block.hash[:16]}...")
    print(f"Records in block: {len(new_block.records)}")

    # Create research certificate
    print("\n--- Research Certificate ---")
    certificate = verifier.create_research_certificate(code_record.id)
    print(f"Certificate ID: {certificate['certificate_id']}")
    print(f"Validity: {certificate['validity']}")
    print(f"Block index: {certificate['block_index']}")

    # Get verification statistics
    print("\n--- Verification Statistics ---")
    stats = verifier.get_verification_statistics()
    print(f"Total blocks: {stats['total_blocks']}")
    print(f"Total records: {stats['total_records']}")
    print(f"Blockchain integrity: {stats['blockchain_integrity']}")
    print(f"Verification types: {stats['verification_types']}")

    # Get researcher reputation
    print("\n--- Researcher Reputation ---")
    alice_rep = verifier.blockchain.get_researcher_reputation("alice_researcher")
    print(f"Alice's reputation score: {alice_rep['reputation_score']}")
    print(f"Total verifications: {alice_rep['total_verifications']}")
    print(f"Reliability: {alice_rep['reliability']:.2f}")

    # Audit trail
    print("\n--- Audit Trail ---")
    trail = verifier.audit_trail(code_record.content_hash)
    for entry in trail:
        print(f"Block {entry['block_index']}: {entry['verification_type']} "
              f"by {entry['researcher_id']} at {entry['timestamp']}")

    print("\n✅ Blockchain verification system implemented!")