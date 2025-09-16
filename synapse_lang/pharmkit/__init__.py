"""
PharmKit - Drug Discovery Extension for Synapse Language
Professional molecular modeling and cheminformatics toolkit
"""

__version__ = "0.1.0"
__author__ = "SynapseLang Team"

from .docking import AutoDock4, AutoDockVina, DockingEngine, DockingResult, Glide, PoseScorer
from .ml import GenerativeModel, GraphNeuralNetwork, MolecularTransformer, PropertyPredictor
from .molecular import (
    Fingerprint,
    MolecularDescriptor,
    Molecule,
    parse_pdb,
    parse_sdf,
    parse_smiles,
)
from .qsar import ActivityCliff, ADMETPredictor, DescriptorCalculator, ModelValidator, QSARModel
from .screening import (
    CompoundLibrary,
    FragmentBasedDesign,
    HitIdentifier,
    LeadOptimizer,
    VirtualScreener,
)
from .synthesis import ReactionDatabase, ReactionPlanner, RetrosyntheticAnalyzer, RouteOptimizer
from .visualization import (
    DockingVisualizer,
    InteractionPlotter,
    MolecularViewer,
    PharmacophoreMapper,
)

__all__ = [
    # Core molecular
    "Molecule",
    "MolecularDescriptor",
    "Fingerprint",
    "parse_smiles",
    "parse_sdf",
    "parse_pdb",

    # Docking
    "DockingEngine",
    "AutoDockVina",
    "AutoDock4",
    "Glide",
    "DockingResult",
    "PoseScorer",

    # QSAR/QSPR
    "QSARModel",
    "DescriptorCalculator",
    "ADMETPredictor",
    "ActivityCliff",
    "ModelValidator",

    # Synthesis planning
    "ReactionPlanner",
    "RetrosyntheticAnalyzer",
    "RouteOptimizer",
    "ReactionDatabase",

    # Virtual screening
    "VirtualScreener",
    "CompoundLibrary",
    "HitIdentifier",
    "LeadOptimizer",
    "FragmentBasedDesign",

    # Machine learning
    "GraphNeuralNetwork",
    "MolecularTransformer",
    "GenerativeModel",
    "PropertyPredictor",

    # Visualization
    "MolecularViewer",
    "InteractionPlotter",
    "PharmacophoreMapper",
    "DockingVisualizer"
]
