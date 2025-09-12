"""
QSAR/QSPR modeling for drug discovery with uncertainty quantification
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import pandas as pd

from ..uncertainty import UncertainValue
from .molecular import Molecule, MolecularDescriptor


@dataclass
class QSARModel:
    """
    QSAR/QSPR model with uncertainty quantification and validation.
    """
    target_property: str
    descriptor_names: List[str] = field(default_factory=list)
    model: Any = None
    scaler: Optional[StandardScaler] = None
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    uncertainty_model: Any = None
    
    def __post_init__(self):
        """Initialize default model if none provided."""
        if self.model is None:
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
    
    def fit(self, molecules: List[Molecule], 
            activities: List[Union[float, UncertainValue]],
            descriptors: Optional[List[str]] = None,
            scale_features: bool = True) -> 'QSARModel':
        """
        Train QSAR model on molecular data.
        
        Args:
            molecules: List of molecules
            activities: List of activity values (can be uncertain)
            descriptors: List of descriptors to use (None for all)
            scale_features: Whether to standardize features
        """
        # Calculate molecular descriptors
        X = self._calculate_descriptor_matrix(molecules, descriptors)
        
        # Handle uncertain activities
        y, y_uncertainties = self._process_activities(activities)
        
        # Feature scaling
        if scale_features:
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(X)
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Fit main model
        self.model.fit(X_train, y_train)
        
        # Calculate validation metrics
        y_pred = self.model.predict(X_test)
        self.validation_metrics = {
            'r2_score': r2_score(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'cross_val_r2': np.mean(cross_val_score(self.model, X_train, y_train, cv=5))
        }
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            self.feature_importance = dict(zip(self.descriptor_names, importance))
        
        # Train uncertainty model if we have uncertainties
        if any(u > 0 for u in y_uncertainties):
            self._train_uncertainty_model(X_train, y_uncertainties[:len(X_train)])
        
        return self
    
    def predict(self, molecules: List[Molecule], 
                return_uncertainty: bool = True) -> List[Union[float, UncertainValue]]:
        """
        Predict activities for new molecules.
        """
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
        
        X = self._calculate_descriptor_matrix(molecules, self.descriptor_names)
        
        if self.scaler:
            X = self.scaler.transform(X)
        
        predictions = self.model.predict(X)
        
        if return_uncertainty:
            uncertainties = self._predict_uncertainties(X)
            return [UncertainValue(pred, unc) for pred, unc in zip(predictions, uncertainties)]
        
        return predictions.tolist()
    
    def applicability_domain(self, molecules: List[Molecule]) -> List[bool]:
        """
        Check if molecules are within the model's applicability domain.
        """
        X = self._calculate_descriptor_matrix(molecules, self.descriptor_names)
        
        if self.scaler:
            X = self.scaler.transform(X)
        
        # Simple leverage-based approach
        # In production, use more sophisticated methods
        leverage = np.diag(X @ np.linalg.pinv(X.T @ X) @ X.T)
        threshold = 3 * len(self.descriptor_names) / len(X)
        
        return (leverage < threshold).tolist()
    
    def _calculate_descriptor_matrix(self, molecules: List[Molecule], 
                                   descriptor_names: Optional[List[str]] = None) -> np.ndarray:
        """Calculate descriptor matrix for molecules."""
        descriptors_list = []
        
        for molecule in molecules:
            desc_dict = MolecularDescriptor.calculate_all(molecule)
            
            # Filter descriptors if specified
            if descriptor_names:
                desc_dict = {k: v for k, v in desc_dict.items() if k in descriptor_names}
            
            descriptors_list.append(list(desc_dict.values()))
        
        # Store descriptor names if not already set
        if not self.descriptor_names and descriptors_list:
            sample_desc = MolecularDescriptor.calculate_all(molecules[0])
            if descriptor_names:
                self.descriptor_names = [k for k in sample_desc.keys() if k in descriptor_names]
            else:
                self.descriptor_names = list(sample_desc.keys())
        
        return np.array(descriptors_list)
    
    def _process_activities(self, activities: List[Union[float, UncertainValue]]) -> Tuple[np.ndarray, List[float]]:
        """Process activity values and extract uncertainties."""
        y_values = []
        uncertainties = []
        
        for activity in activities:
            if isinstance(activity, UncertainValue):
                y_values.append(activity.value)
                uncertainties.append(activity.uncertainty)
            else:
                y_values.append(float(activity))
                uncertainties.append(0.0)
        
        return np.array(y_values), uncertainties
    
    def _train_uncertainty_model(self, X: np.ndarray, uncertainties: List[float]):
        """Train a model to predict uncertainties."""
        if any(u > 0 for u in uncertainties):
            self.uncertainty_model = RandomForestRegressor(
                n_estimators=50,
                random_state=42
            )
            self.uncertainty_model.fit(X, uncertainties)
    
    def _predict_uncertainties(self, X: np.ndarray) -> List[float]:
        """Predict uncertainties for new data."""
        if self.uncertainty_model is not None:
            return self.uncertainty_model.predict(X).tolist()
        
        # Default uncertainty based on model performance
        base_uncertainty = self.validation_metrics.get('rmse', 0.5)
        return [base_uncertainty] * len(X)


class DescriptorCalculator:
    """
    Advanced molecular descriptor calculator.
    """
    
    @staticmethod
    def physicochemical_descriptors(molecule: Molecule) -> Dict[str, float]:
        """Calculate physicochemical descriptors."""
        return {
            'molecular_weight': molecule.molecular_weight,
            'logp': molecule.logp,
            'hbd': molecule.hbd,
            'hba': molecule.hba,
            'tpsa': molecule.tpsa,
            'rotatable_bonds': molecule.rotatable_bonds,
            'aromatic_ratio': DescriptorCalculator._aromatic_ratio(molecule),
            'sp3_fraction': DescriptorCalculator._sp3_fraction(molecule),
            'complexity': DescriptorCalculator._molecular_complexity(molecule)
        }
    
    @staticmethod
    def topological_descriptors(molecule: Molecule) -> Dict[str, float]:
        """Calculate topological descriptors."""
        return {
            'wiener_index': DescriptorCalculator._wiener_index(molecule),
            'balaban_j': DescriptorCalculator._balaban_j(molecule),
            'zagreb_m1': DescriptorCalculator._zagreb_m1(molecule),
            'zagreb_m2': DescriptorCalculator._zagreb_m2(molecule)
        }
    
    @staticmethod
    def electronic_descriptors(molecule: Molecule) -> Dict[str, float]:
        """Calculate electronic descriptors."""
        return {
            'homo_energy': DescriptorCalculator._homo_energy(molecule),
            'lumo_energy': DescriptorCalculator._lumo_energy(molecule),
            'electronegativity': DescriptorCalculator._electronegativity(molecule),
            'hardness': DescriptorCalculator._hardness(molecule)
        }
    
    @staticmethod
    def _aromatic_ratio(molecule: Molecule) -> float:
        """Calculate ratio of aromatic atoms."""
        # Simplified calculation
        aromatic_count = molecule.smiles.count('c')
        total_carbons = molecule.smiles.count('C') + molecule.smiles.count('c')
        return aromatic_count / max(total_carbons, 1)
    
    @staticmethod
    def _sp3_fraction(molecule: Molecule) -> float:
        """Calculate fraction of sp3 carbons."""
        # Simplified estimation
        aliphatic_count = molecule.smiles.count('C')
        total_carbons = molecule.smiles.count('C') + molecule.smiles.count('c')
        return aliphatic_count / max(total_carbons, 1)
    
    @staticmethod
    def _molecular_complexity(molecule: Molecule) -> float:
        """Calculate molecular complexity score."""
        # Simple complexity based on SMILES length and special characters
        complexity = len(molecule.smiles)
        complexity += molecule.smiles.count('(') * 2  # Branching
        complexity += molecule.smiles.count('[') * 3  # Special atoms
        complexity += molecule.smiles.count('=') * 1.5  # Double bonds
        complexity += molecule.smiles.count('#') * 2.5  # Triple bonds
        return complexity
    
    # Placeholder methods for advanced descriptors
    @staticmethod
    def _wiener_index(molecule: Molecule) -> float:
        """Calculate Wiener index (sum of distances between all atom pairs)."""
        return float(len(molecule.smiles))  # Placeholder
    
    @staticmethod
    def _balaban_j(molecule: Molecule) -> float:
        """Calculate Balaban J index."""
        return 1.0  # Placeholder
    
    @staticmethod
    def _zagreb_m1(molecule: Molecule) -> float:
        """Calculate first Zagreb index."""
        return float(molecule.molecular_weight / 50)  # Placeholder
    
    @staticmethod
    def _zagreb_m2(molecule: Molecule) -> float:
        """Calculate second Zagreb index."""
        return float(molecule.molecular_weight / 100)  # Placeholder
    
    @staticmethod
    def _homo_energy(molecule: Molecule) -> float:
        """Calculate HOMO energy."""
        return -8.0 - np.random.random()  # Placeholder
    
    @staticmethod
    def _lumo_energy(molecule: Molecule) -> float:
        """Calculate LUMO energy."""
        return -2.0 + np.random.random()  # Placeholder
    
    @staticmethod
    def _electronegativity(molecule: Molecule) -> float:
        """Calculate electronegativity."""
        return 2.5 + np.random.random()  # Placeholder
    
    @staticmethod
    def _hardness(molecule: Molecule) -> float:
        """Calculate chemical hardness."""
        return 3.0 + np.random.random()  # Placeholder


class ADMETPredictor:
    """
    ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) property predictor.
    """
    
    def __init__(self):
        self.models = {
            'solubility': None,
            'permeability': None,
            'bioavailability': None,
            'clearance': None,
            'half_life': None,
            'herg_inhibition': None,
            'cyp_inhibition': None,
            'hepatotoxicity': None,
            'mutagenicity': None
        }
    
    def predict_admet(self, molecules: List[Molecule]) -> Dict[str, List[UncertainValue]]:
        """
        Predict comprehensive ADMET properties.
        """
        results = {}
        
        for property_name in self.models.keys():
            results[property_name] = self._predict_property(molecules, property_name)
        
        return results
    
    def _predict_property(self, molecules: List[Molecule], 
                         property_name: str) -> List[UncertainValue]:
        """Predict a single ADMET property."""
        predictions = []
        
        for molecule in molecules:
            # Generate realistic predictions based on molecular properties
            value, uncertainty = self._generate_admet_prediction(molecule, property_name)
            predictions.append(UncertainValue(value, uncertainty))
        
        return predictions
    
    def _generate_admet_prediction(self, molecule: Molecule, 
                                 property_name: str) -> Tuple[float, float]:
        """Generate ADMET prediction with uncertainty."""
        
        # Solubility (log S)
        if property_name == 'solubility':
            # Correlation with lipophilicity
            base_value = -0.5 * molecule.logp - 0.01 * molecule.molecular_weight + 2.0
            uncertainty = 0.5 + 0.1 * abs(molecule.logp)
            return base_value, uncertainty
        
        # Permeability (log Pe)
        elif property_name == 'permeability':
            # Correlation with PSA and MW
            base_value = -0.02 * molecule.tpsa - 0.001 * molecule.molecular_weight + 1.0
            uncertainty = 0.3
            return base_value, uncertainty
        
        # Oral bioavailability (%)
        elif property_name == 'bioavailability':
            # Rule-of-five based estimation
            violations = molecule.lipinski_violations()
            base_value = max(10, 80 - violations * 20)
            uncertainty = 15 + violations * 5
            return base_value, uncertainty
        
        # Clearance (L/hr/kg)
        elif property_name == 'clearance':
            base_value = 1.5 + np.random.exponential(1.0)
            uncertainty = 0.5
            return base_value, uncertainty
        
        # Half-life (hours)
        elif property_name == 'half_life':
            base_value = 2.0 + np.random.exponential(5.0)
            uncertainty = 2.0
            return base_value, uncertainty
        
        # hERG inhibition (IC50, µM)
        elif property_name == 'herg_inhibition':
            # Correlated with lipophilicity
            base_value = 10 ** (1.0 - 0.5 * molecule.logp)
            uncertainty = base_value * 0.3
            return base_value, uncertainty
        
        # CYP inhibition probability
        elif property_name == 'cyp_inhibition':
            base_value = min(0.9, max(0.1, 0.3 + 0.1 * molecule.logp))
            uncertainty = 0.2
            return base_value, uncertainty
        
        # Hepatotoxicity probability
        elif property_name == 'hepatotoxicity':
            base_value = min(0.8, max(0.05, 0.1 + 0.05 * molecule.molecular_weight / 100))
            uncertainty = 0.15
            return base_value, uncertainty
        
        # Mutagenicity probability
        elif property_name == 'mutagenicity':
            base_value = 0.1 + np.random.random() * 0.3
            uncertainty = 0.1
            return base_value, uncertainty
        
        else:
            return 0.0, 1.0


class ActivityCliff:
    """
    Identify and analyze activity cliffs in QSAR datasets.
    """
    
    @staticmethod
    def find_cliffs(molecules: List[Molecule], 
                   activities: List[float],
                   similarity_threshold: float = 0.85,
                   activity_threshold: float = 1.0) -> List[Tuple[int, int, float, float]]:
        """
        Find activity cliffs in the dataset.
        
        Returns:
            List of (mol1_idx, mol2_idx, similarity, activity_diff) tuples
        """
        cliffs = []
        
        for i in range(len(molecules)):
            for j in range(i + 1, len(molecules)):
                similarity = molecules[i].similarity(molecules[j])
                activity_diff = abs(activities[i] - activities[j])
                
                if (similarity >= similarity_threshold and 
                    activity_diff >= activity_threshold):
                    cliffs.append((i, j, similarity, activity_diff))
        
        return sorted(cliffs, key=lambda x: x[3], reverse=True)
    
    @staticmethod
    def cliff_analysis(cliffs: List[Tuple[int, int, float, float]], 
                      molecules: List[Molecule]) -> Dict[str, Any]:
        """
        Analyze activity cliffs to identify important structural features.
        """
        analysis = {
            'total_cliffs': len(cliffs),
            'avg_similarity': np.mean([c[2] for c in cliffs]) if cliffs else 0.0,
            'avg_activity_diff': np.mean([c[3] for c in cliffs]) if cliffs else 0.0,
            'structural_alerts': []
        }
        
        # Identify common structural patterns in cliff pairs
        if cliffs:
            # Simple analysis - look for common substructures
            cliff_molecules = []
            for i, j, _, _ in cliffs[:10]:  # Top 10 cliffs
                cliff_molecules.extend([molecules[i], molecules[j]])
            
            # Count functional groups (simplified)
            group_counts = {}
            for mol in cliff_molecules:
                groups = ActivityCliff._identify_functional_groups(mol)
                for group in groups:
                    group_counts[group] = group_counts.get(group, 0) + 1
            
            # Find overrepresented groups
            total_mols = len(molecules)
            for group, count in group_counts.items():
                frequency = count / len(cliff_molecules)
                if frequency > 0.5:  # Present in >50% of cliff molecules
                    analysis['structural_alerts'].append(group)
        
        return analysis
    
    @staticmethod
    def _identify_functional_groups(molecule: Molecule) -> List[str]:
        """Identify functional groups in molecule."""
        groups = []
        smiles = molecule.smiles
        
        # Simple pattern matching for common groups
        if 'OH' in smiles or 'O' in smiles:
            groups.append('alcohol/ether')
        if 'C=O' in smiles:
            groups.append('carbonyl')
        if 'N' in smiles:
            groups.append('amine/imine')
        if 'S' in smiles:
            groups.append('sulfur')
        if 'F' in smiles:
            groups.append('fluorine')
        if 'Cl' in smiles:
            groups.append('chlorine')
        if 'Br' in smiles:
            groups.append('bromine')
        
        return groups


class ModelValidator:
    """
    Validate QSAR models using various metrics and statistical tests.
    """
    
    @staticmethod
    def external_validation(model: QSARModel, 
                          test_molecules: List[Molecule],
                          test_activities: List[float]) -> Dict[str, float]:
        """
        Perform external validation of QSAR model.
        """
        predictions = model.predict(test_molecules, return_uncertainty=False)
        
        # Calculate metrics
        r2 = r2_score(test_activities, predictions)
        rmse = np.sqrt(mean_squared_error(test_activities, predictions))
        mae = mean_absolute_error(test_activities, predictions)
        
        # Q² external
        ss_res = np.sum((test_activities - predictions) ** 2)
        ss_tot = np.sum((test_activities - np.mean(test_activities)) ** 2)
        q2_ext = 1 - (ss_res / ss_tot)
        
        # Concordance correlation coefficient
        ccc = ModelValidator._concordance_correlation(test_activities, predictions)
        
        return {
            'r2_external': r2,
            'rmse_external': rmse,
            'mae_external': mae,
            'q2_external': q2_ext,
            'ccc': ccc,
            'n_test': len(test_activities)
        }
    
    @staticmethod
    def y_scrambling(model_class, X: np.ndarray, y: np.ndarray, 
                    n_iterations: int = 100) -> Dict[str, float]:
        """
        Perform Y-scrambling validation.
        """
        original_scores = []
        scrambled_scores = []
        
        for _ in range(n_iterations):
            # Train on original data
            model_orig = model_class()
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            model_orig.fit(X_train, y_train)
            orig_score = r2_score(y_test, model_orig.predict(X_test))
            original_scores.append(orig_score)
            
            # Train on scrambled data
            y_scrambled = np.random.permutation(y)
            y_train_scram, y_test_scram = train_test_split(y_scrambled, test_size=0.2)[1::2]
            model_scram = model_class()
            model_scram.fit(X_train, y_train_scram)
            scram_score = r2_score(y_test_scram, model_scram.predict(X_test))
            scrambled_scores.append(scram_score)
        
        return {
            'original_r2_mean': np.mean(original_scores),
            'original_r2_std': np.std(original_scores),
            'scrambled_r2_mean': np.mean(scrambled_scores),
            'scrambled_r2_std': np.std(scrambled_scores),
            'scrambled_max': np.max(scrambled_scores)
        }
    
    @staticmethod
    def _concordance_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate concordance correlation coefficient."""
        mean_true = np.mean(y_true)
        mean_pred = np.mean(y_pred)
        var_true = np.var(y_true)
        var_pred = np.var(y_pred)
        covar = np.mean((y_true - mean_true) * (y_pred - mean_pred))
        
        ccc = 2 * covar / (var_true + var_pred + (mean_true - mean_pred)**2)
        return ccc