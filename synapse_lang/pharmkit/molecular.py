"""
Molecular representation and manipulation for drug discovery
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import hashlib
import json

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, Crippen
    from rdkit.Chem import AllChem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False


@dataclass
class Molecule:
    """
    Core molecular representation with uncertainty-aware properties.
    """
    smiles: str
    name: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    conformers: List[np.ndarray] = field(default_factory=list)
    _mol: Any = None  # RDKit mol object
    _fingerprint: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Initialize RDKit molecule if available."""
        if HAS_RDKIT and self._mol is None:
            self._mol = Chem.MolFromSmiles(self.smiles)
            if self._mol is None:
                raise ValueError(f"Invalid SMILES: {self.smiles}")
    
    @property
    def molecular_weight(self) -> float:
        """Calculate molecular weight."""
        if HAS_RDKIT and self._mol:
            return Descriptors.MolWt(self._mol)
        # Fallback estimation
        return len(self.smiles) * 12.0  # Very rough estimate
    
    @property
    def logp(self) -> float:
        """Calculate LogP (lipophilicity)."""
        if HAS_RDKIT and self._mol:
            return Crippen.MolLogP(self._mol)
        return self.properties.get('logp', 0.0)
    
    @property
    def hbd(self) -> int:
        """Number of hydrogen bond donors."""
        if HAS_RDKIT and self._mol:
            return Lipinski.NumHDonors(self._mol)
        return self.properties.get('hbd', 0)
    
    @property
    def hba(self) -> int:
        """Number of hydrogen bond acceptors."""
        if HAS_RDKIT and self._mol:
            return Lipinski.NumHAcceptors(self._mol)
        return self.properties.get('hba', 0)
    
    @property
    def tpsa(self) -> float:
        """Topological polar surface area."""
        if HAS_RDKIT and self._mol:
            return Descriptors.TPSA(self._mol)
        return self.properties.get('tpsa', 0.0)
    
    @property
    def rotatable_bonds(self) -> int:
        """Number of rotatable bonds."""
        if HAS_RDKIT and self._mol:
            return Lipinski.NumRotatableBonds(self._mol)
        return self.properties.get('rotatable_bonds', 0)
    
    def lipinski_violations(self) -> int:
        """Check Lipinski's Rule of Five violations."""
        violations = 0
        if self.molecular_weight > 500:
            violations += 1
        if self.logp > 5:
            violations += 1
        if self.hbd > 5:
            violations += 1
        if self.hba > 10:
            violations += 1
        return violations
    
    def generate_conformers(self, n_conformers: int = 10, 
                          energy_window: float = 20.0) -> List[np.ndarray]:
        """Generate 3D conformers."""
        if HAS_RDKIT and self._mol:
            mol_h = Chem.AddHs(self._mol)
            conf_ids = AllChem.EmbedMultipleConfs(
                mol_h, 
                numConfs=n_conformers,
                randomSeed=42
            )
            
            # Optimize conformers
            for conf_id in conf_ids:
                AllChem.UFFOptimizeMolecule(mol_h, confId=conf_id)
            
            # Extract coordinates
            conformers = []
            for conf_id in conf_ids:
                conf = mol_h.GetConformer(conf_id)
                coords = conf.GetPositions()
                conformers.append(coords)
            
            self.conformers = conformers
            return conformers
        
        # Fallback: return empty list
        return []
    
    def get_fingerprint(self, fp_type: str = "morgan", radius: int = 2, 
                       n_bits: int = 2048) -> np.ndarray:
        """Generate molecular fingerprint."""
        if self._fingerprint is not None:
            return self._fingerprint
        
        if HAS_RDKIT and self._mol:
            if fp_type == "morgan":
                fp = AllChem.GetMorganFingerprintAsBitVect(
                    self._mol, radius, nBits=n_bits
                )
            elif fp_type == "maccs":
                from rdkit.Chem import MACCSkeys
                fp = MACCSkeys.GenMACCSKeys(self._mol)
            else:
                fp = AllChem.RDKFingerprint(self._mol)
            
            self._fingerprint = np.array(fp)
            return self._fingerprint
        
        # Fallback: hash-based fingerprint
        hash_obj = hashlib.sha256(self.smiles.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        fp = np.zeros(n_bits)
        for i in range(n_bits):
            fp[i] = (hash_int >> i) & 1
        self._fingerprint = fp
        return fp
    
    def similarity(self, other: 'Molecule', metric: str = "tanimoto") -> float:
        """Calculate molecular similarity."""
        fp1 = self.get_fingerprint()
        fp2 = other.get_fingerprint()
        
        if metric == "tanimoto":
            intersection = np.sum(fp1 & fp2)
            union = np.sum(fp1 | fp2)
            return intersection / union if union > 0 else 0.0
        elif metric == "dice":
            intersection = np.sum(fp1 & fp2)
            return 2 * intersection / (np.sum(fp1) + np.sum(fp2))
        else:
            raise ValueError(f"Unknown similarity metric: {metric}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize molecule to dictionary."""
        return {
            'smiles': self.smiles,
            'name': self.name,
            'properties': self.properties,
            'molecular_weight': self.molecular_weight,
            'logp': self.logp,
            'hbd': self.hbd,
            'hba': self.hba,
            'tpsa': self.tpsa,
            'rotatable_bonds': self.rotatable_bonds,
            'lipinski_violations': self.lipinski_violations()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Molecule':
        """Create molecule from dictionary."""
        mol = cls(
            smiles=data['smiles'],
            name=data.get('name'),
            properties=data.get('properties', {})
        )
        return mol


class MolecularDescriptor:
    """
    Calculate molecular descriptors for QSAR/QSPR modeling.
    """
    
    @staticmethod
    def calculate_all(molecule: Molecule) -> Dict[str, float]:
        """Calculate all available descriptors."""
        descriptors = {
            'molecular_weight': molecule.molecular_weight,
            'logp': molecule.logp,
            'hbd': molecule.hbd,
            'hba': molecule.hba,
            'tpsa': molecule.tpsa,
            'rotatable_bonds': molecule.rotatable_bonds,
            'lipinski_violations': molecule.lipinski_violations()
        }
        
        if HAS_RDKIT and molecule._mol:
            # Add more RDKit descriptors
            descriptors.update({
                'num_rings': Lipinski.NumAromaticRings(molecule._mol),
                'num_heteroatoms': Lipinski.NumHeteroatoms(molecule._mol),
                'formal_charge': Chem.GetFormalCharge(molecule._mol),
                'num_heavy_atoms': molecule._mol.GetNumHeavyAtoms(),
                'fraction_csp3': Lipinski.FractionCsp3(molecule._mol),
            })
        
        return descriptors
    
    @staticmethod
    def calculate_pharmacophore(molecule: Molecule) -> Dict[str, List[int]]:
        """Extract pharmacophore features."""
        features = {
            'donors': [],
            'acceptors': [],
            'aromatic': [],
            'hydrophobic': [],
            'positive': [],
            'negative': []
        }
        
        if HAS_RDKIT and molecule._mol:
            # Simple pharmacophore extraction
            for i, atom in enumerate(molecule._mol.GetAtoms()):
                if atom.GetAtomicNum() in [7, 8] and atom.GetTotalNumHs() > 0:
                    features['donors'].append(i)
                if atom.GetAtomicNum() in [7, 8, 16]:
                    features['acceptors'].append(i)
                if atom.GetIsAromatic():
                    features['aromatic'].append(i)
                if atom.GetAtomicNum() == 6:
                    features['hydrophobic'].append(i)
        
        return features


class Fingerprint:
    """
    Molecular fingerprint generator with multiple algorithms.
    """
    
    @staticmethod
    def morgan(molecule: Molecule, radius: int = 2, n_bits: int = 2048) -> np.ndarray:
        """Morgan (circular) fingerprint."""
        return molecule.get_fingerprint("morgan", radius, n_bits)
    
    @staticmethod
    def maccs(molecule: Molecule) -> np.ndarray:
        """MACCS keys fingerprint."""
        return molecule.get_fingerprint("maccs")
    
    @staticmethod
    def pharmacophore(molecule: Molecule, n_bits: int = 2048) -> np.ndarray:
        """Pharmacophore fingerprint."""
        fp = np.zeros(n_bits)
        features = MolecularDescriptor.calculate_pharmacophore(molecule)
        
        # Simple encoding of pharmacophore features
        for feature_type, atoms in features.items():
            for atom in atoms:
                # Hash feature type and atom index to bit position
                hash_str = f"{feature_type}_{atom}"
                hash_val = int(hashlib.md5(hash_str.encode()).hexdigest(), 16)
                bit_pos = hash_val % n_bits
                fp[bit_pos] = 1
        
        return fp


def parse_smiles(smiles: str, name: Optional[str] = None) -> Molecule:
    """Parse SMILES string to Molecule."""
    return Molecule(smiles=smiles, name=name)


def parse_sdf(sdf_content: str) -> List[Molecule]:
    """Parse SDF file content to list of Molecules."""
    molecules = []
    
    if HAS_RDKIT:
        suppl = Chem.SDMolSupplier()
        suppl.SetData(sdf_content)
        for mol in suppl:
            if mol is not None:
                smiles = Chem.MolToSmiles(mol)
                name = mol.GetProp("_Name") if mol.HasProp("_Name") else None
                molecules.append(Molecule(smiles=smiles, name=name))
    else:
        # Basic SDF parsing without RDKit
        entries = sdf_content.split("$$$$")
        for entry in entries:
            if entry.strip():
                # Try to extract name from first line
                lines = entry.strip().split('\n')
                name = lines[0] if lines else None
                # Create placeholder molecule
                molecules.append(Molecule(smiles="C", name=name))
    
    return molecules


def parse_pdb(pdb_content: str) -> Molecule:
    """Parse PDB file content to Molecule."""
    if HAS_RDKIT:
        mol = Chem.MolFromPDBBlock(pdb_content)
        if mol:
            smiles = Chem.MolToSmiles(mol)
            return Molecule(smiles=smiles)
    
    # Fallback: create placeholder
    return Molecule(smiles="C", name="PDB_molecule")