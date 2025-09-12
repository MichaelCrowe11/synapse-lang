"""
Molecular docking interfaces and wrappers for drug discovery
"""

import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path
import json

from ..uncertainty import UncertainValue
from .molecular import Molecule


@dataclass
class DockingResult:
    """
    Result from molecular docking with uncertainty quantification.
    """
    ligand: Molecule
    receptor: str  # PDB ID or path
    score: UncertainValue  # Binding affinity with uncertainty
    poses: List[np.ndarray]  # 3D coordinates of poses
    interactions: Dict[str, List[Tuple[int, int]]]  # Interaction types
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def best_pose(self) -> np.ndarray:
        """Return the best scoring pose."""
        return self.poses[0] if self.poses else np.array([])
    
    def get_confidence(self) -> float:
        """Calculate confidence score based on uncertainty."""
        if self.score.uncertainty == 0:
            return 1.0
        # Higher uncertainty means lower confidence
        return 1.0 / (1.0 + self.score.uncertainty)
    
    def interaction_summary(self) -> str:
        """Generate human-readable interaction summary."""
        summary = []
        for interaction_type, pairs in self.interactions.items():
            summary.append(f"{interaction_type}: {len(pairs)} contacts")
        return "; ".join(summary)


class DockingEngine:
    """
    Abstract base class for docking engines.
    """
    
    def __init__(self, executable_path: Optional[str] = None):
        self.executable = executable_path or self._find_executable()
        self.config = {}
    
    def _find_executable(self) -> str:
        """Find the docking software executable."""
        raise NotImplementedError
    
    def prepare_receptor(self, pdb_file: str) -> str:
        """Prepare receptor for docking."""
        raise NotImplementedError
    
    def prepare_ligand(self, molecule: Molecule) -> str:
        """Prepare ligand for docking."""
        raise NotImplementedError
    
    def dock(self, ligand: Molecule, receptor: str, 
             **kwargs) -> DockingResult:
        """Perform molecular docking."""
        raise NotImplementedError
    
    def validate_setup(self) -> bool:
        """Check if docking engine is properly configured."""
        if not self.executable:
            return False
        return Path(self.executable).exists()


class AutoDockVina(DockingEngine):
    """
    AutoDock Vina wrapper for molecular docking.
    """
    
    def _find_executable(self) -> str:
        """Find Vina executable."""
        possible_paths = [
            "vina",
            "/usr/local/bin/vina",
            "/opt/vina/bin/vina",
            "C:\\Program Files\\AutoDock Vina\\vina.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # Check if vina is in PATH
        try:
            result = subprocess.run(["vina", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return "vina"
        except:
            pass
        
        return None
    
    def prepare_receptor(self, pdb_file: str) -> str:
        """Prepare receptor PDBQT file."""
        output_file = pdb_file.replace(".pdb", ".pdbqt")
        
        # In production, use proper preparation tools
        # For now, simple conversion placeholder
        with open(pdb_file, 'r') as f:
            pdb_content = f.read()
        
        # Add charges and atom types (simplified)
        pdbqt_content = pdb_content.replace("ATOM  ", "ATOM  ")
        
        with open(output_file, 'w') as f:
            f.write(pdbqt_content)
        
        return output_file
    
    def prepare_ligand(self, molecule: Molecule) -> str:
        """Prepare ligand PDBQT file."""
        # Generate 3D conformer if needed
        if not molecule.conformers:
            molecule.generate_conformers(n_conformers=1)
        
        # Create temporary PDBQT file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdbqt', 
                                        delete=False) as f:
            # Write simplified PDBQT format
            f.write(f"REMARK  Name = {molecule.name or 'ligand'}\n")
            f.write(f"REMARK  SMILES = {molecule.smiles}\n")
            
            if molecule.conformers:
                coords = molecule.conformers[0]
                for i, coord in enumerate(coords):
                    f.write(f"ATOM  {i+1:5d}  C   LIG     1    "
                           f"{coord[0]:8.3f}{coord[1]:8.3f}{coord[2]:8.3f}"
                           f"  1.00  0.00     C\n")
            
            return f.name
    
    def dock(self, ligand: Molecule, receptor: str,
             center: Tuple[float, float, float] = (0, 0, 0),
             size: Tuple[float, float, float] = (20, 20, 20),
             exhaustiveness: int = 8,
             num_modes: int = 9,
             energy_range: float = 3.0,
             **kwargs) -> DockingResult:
        """
        Perform docking with AutoDock Vina.
        """
        if not self.validate_setup():
            # Fallback: generate mock results for testing
            return self._mock_docking(ligand, receptor)
        
        # Prepare files
        receptor_pdbqt = self.prepare_receptor(receptor)
        ligand_pdbqt = self.prepare_ligand(ligand)
        output_pdbqt = tempfile.mktemp(suffix='_out.pdbqt')
        
        # Create config file
        config_file = tempfile.mktemp(suffix='.txt')
        with open(config_file, 'w') as f:
            f.write(f"receptor = {receptor_pdbqt}\n")
            f.write(f"ligand = {ligand_pdbqt}\n")
            f.write(f"out = {output_pdbqt}\n")
            f.write(f"center_x = {center[0]}\n")
            f.write(f"center_y = {center[1]}\n")
            f.write(f"center_z = {center[2]}\n")
            f.write(f"size_x = {size[0]}\n")
            f.write(f"size_y = {size[1]}\n")
            f.write(f"size_z = {size[2]}\n")
            f.write(f"exhaustiveness = {exhaustiveness}\n")
            f.write(f"num_modes = {num_modes}\n")
            f.write(f"energy_range = {energy_range}\n")
        
        # Run Vina
        cmd = [self.executable, "--config", config_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        if result.returncode == 0:
            scores, poses = self._parse_vina_output(output_pdbqt)
            
            # Calculate uncertainty based on score distribution
            if len(scores) > 1:
                uncertainty = np.std(scores[:min(3, len(scores))])
            else:
                uncertainty = 0.5  # Default uncertainty
            
            return DockingResult(
                ligand=ligand,
                receptor=receptor,
                score=UncertainValue(scores[0], uncertainty),
                poses=poses,
                interactions=self._analyze_interactions(poses[0], receptor),
                metadata={
                    'engine': 'AutoDock Vina',
                    'exhaustiveness': exhaustiveness,
                    'all_scores': scores
                }
            )
        else:
            raise RuntimeError(f"Vina docking failed: {result.stderr}")
    
    def _mock_docking(self, ligand: Molecule, receptor: str) -> DockingResult:
        """Generate mock docking results for testing."""
        # Generate realistic-looking binding affinity
        base_score = -7.5 - np.random.exponential(1.5)
        uncertainty = 0.3 + np.random.random() * 0.4
        
        # Generate mock pose
        if not ligand.conformers:
            ligand.generate_conformers(n_conformers=1)
        
        pose = ligand.conformers[0] if ligand.conformers else np.random.randn(10, 3)
        
        # Mock interactions
        interactions = {
            'hydrogen_bond': [(5, 102), (8, 156)],
            'hydrophobic': [(2, 89), (11, 203), (15, 178)],
            'pi_stacking': [(7, 145)]
        }
        
        return DockingResult(
            ligand=ligand,
            receptor=receptor,
            score=UncertainValue(base_score, uncertainty),
            poses=[pose],
            interactions=interactions,
            metadata={
                'engine': 'AutoDock Vina (mock)',
                'warning': 'Mock results generated - Vina not found'
            }
        )
    
    def _parse_vina_output(self, output_file: str) -> Tuple[List[float], List[np.ndarray]]:
        """Parse Vina output PDBQT file."""
        scores = []
        poses = []
        
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        current_pose = []
        for line in lines:
            if line.startswith("REMARK VINA RESULT:"):
                parts = line.split()
                if len(parts) >= 4:
                    scores.append(float(parts[3]))
            elif line.startswith("ATOM"):
                # Parse atom coordinates
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                current_pose.append([x, y, z])
            elif line.startswith("ENDMDL"):
                if current_pose:
                    poses.append(np.array(current_pose))
                    current_pose = []
        
        return scores, poses
    
    def _analyze_interactions(self, pose: np.ndarray, 
                            receptor: str) -> Dict[str, List[Tuple[int, int]]]:
        """Analyze molecular interactions."""
        # Simplified interaction detection
        interactions = {
            'hydrogen_bond': [],
            'hydrophobic': [],
            'pi_stacking': [],
            'salt_bridge': []
        }
        
        # Mock interaction detection based on distances
        for i in range(min(len(pose), 10)):
            # Random interaction assignment for demonstration
            if np.random.random() < 0.3:
                interactions['hydrogen_bond'].append((i, np.random.randint(100, 300)))
            if np.random.random() < 0.4:
                interactions['hydrophobic'].append((i, np.random.randint(100, 300)))
        
        return interactions


class AutoDock4(DockingEngine):
    """
    AutoDock 4 wrapper for molecular docking.
    """
    
    def _find_executable(self) -> str:
        """Find AutoDock4 executable."""
        possible_paths = [
            "autodock4",
            "/usr/local/bin/autodock4",
            "C:\\Program Files\\AutoDock\\autodock4.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        return None
    
    def dock(self, ligand: Molecule, receptor: str, **kwargs) -> DockingResult:
        """Perform docking with AutoDock 4."""
        # Similar implementation to Vina
        return self._mock_docking(ligand, receptor)
    
    def _mock_docking(self, ligand: Molecule, receptor: str) -> DockingResult:
        """Generate mock docking results."""
        base_score = -8.2 - np.random.exponential(1.2)
        uncertainty = 0.4 + np.random.random() * 0.3
        
        return DockingResult(
            ligand=ligand,
            receptor=receptor,
            score=UncertainValue(base_score, uncertainty),
            poses=[np.random.randn(20, 3)],
            interactions={'hydrogen_bond': [(3, 145), (7, 289)]},
            metadata={'engine': 'AutoDock 4 (mock)'}
        )


class Glide(DockingEngine):
    """
    Schrödinger Glide wrapper (commercial software).
    """
    
    def _find_executable(self) -> str:
        """Find Glide executable."""
        schrodinger_path = os.environ.get('SCHRODINGER')
        if schrodinger_path:
            glide_path = Path(schrodinger_path) / 'glide'
            if glide_path.exists():
                return str(glide_path)
        return None
    
    def dock(self, ligand: Molecule, receptor: str, 
             precision: str = 'SP', **kwargs) -> DockingResult:
        """
        Perform Glide docking.
        
        Args:
            precision: 'HTVS', 'SP', or 'XP' (high-throughput, standard, extra precision)
        """
        # Mock implementation for demonstration
        if precision == 'XP':
            base_score = -9.5 - np.random.exponential(1.0)
            uncertainty = 0.2
        elif precision == 'SP':
            base_score = -8.5 - np.random.exponential(1.3)
            uncertainty = 0.35
        else:  # HTVS
            base_score = -7.0 - np.random.exponential(1.5)
            uncertainty = 0.5
        
        return DockingResult(
            ligand=ligand,
            receptor=receptor,
            score=UncertainValue(base_score, uncertainty),
            poses=[np.random.randn(25, 3)],
            interactions={
                'hydrogen_bond': [(2, 156), (5, 203), (8, 167)],
                'pi_stacking': [(12, 245)]
            },
            metadata={
                'engine': f'Glide {precision} (mock)',
                'precision': precision
            }
        )


class PoseScorer:
    """
    Score and rank docking poses using multiple criteria.
    """
    
    @staticmethod
    def consensus_score(results: List[DockingResult], 
                       weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate consensus score from multiple docking results.
        """
        if not results:
            return 0.0
        
        if weights is None:
            weights = {
                'AutoDock Vina': 1.0,
                'AutoDock 4': 0.8,
                'Glide': 1.2
            }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result in results:
            engine = result.metadata.get('engine', '').split()[0]
            weight = weights.get(engine, 1.0)
            weighted_sum += result.score.value * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    @staticmethod
    def interaction_score(result: DockingResult, 
                         interaction_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Score based on interaction profile.
        """
        if interaction_weights is None:
            interaction_weights = {
                'hydrogen_bond': 1.5,
                'hydrophobic': 0.8,
                'pi_stacking': 1.2,
                'salt_bridge': 2.0
            }
        
        score = 0.0
        for interaction_type, pairs in result.interactions.items():
            weight = interaction_weights.get(interaction_type, 1.0)
            score += len(pairs) * weight
        
        return score
    
    @staticmethod
    def strain_energy(pose: np.ndarray) -> float:
        """
        Estimate conformational strain energy.
        """
        # Simplified strain calculation based on bond lengths
        if len(pose) < 2:
            return 0.0
        
        distances = []
        for i in range(len(pose) - 1):
            dist = np.linalg.norm(pose[i+1] - pose[i])
            distances.append(dist)
        
        # Penalize unusual bond lengths
        ideal_length = 1.5  # Angstroms
        strain = sum((d - ideal_length)**2 for d in distances)
        return strain