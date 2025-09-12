"""
PharmKit - Drug Discovery Extension for Synapse Language
Professional molecular modeling and cheminformatics toolkit
"""

__version__ = "0.1.0"
__author__ = "SynapseLang Team"

from .molecular import (
    Molecule,
    MolecularDescriptor,
    Fingerprint,
    parse_smiles,
    parse_sdf,
    parse_pdb
)

from .docking import (
    DockingEngine,
    AutoDockVina,
    AutoDock4,
    Glide,
    DockingResult,
    PoseScorer
)

from .qsar import (
    QSARModel,
    DescriptorCalculator,
    ADMETPredictor,
    ActivityCliff,
    ModelValidator
)

from .synthesis import (
    ReactionPlanner,
    RetrosyntheticAnalyzer,
    RouteOptimizer,
    ReactionDatabase
)

from .screening import (
    VirtualScreener,
    CompoundLibrary,
    HitIdentifier,
    LeadOptimizer,
    FragmentBasedDesign
)

from .ml import (
    GraphNeuralNetwork,
    MolecularTransformer,
    GenerativeModel,
    PropertyPredictor
)

from .visualization import (
    MolecularViewer,
    InteractionPlotter,
    PharmacophoreMapper,
    DockingVisualizer
)

__all__ = [
    # Core molecular
    'Molecule',
    'MolecularDescriptor',
    'Fingerprint',
    'parse_smiles',
    'parse_sdf',
    'parse_pdb',
    
    # Docking
    'DockingEngine',
    'AutoDockVina',
    'AutoDock4',
    'Glide',
    'DockingResult',
    'PoseScorer',
    
    # QSAR/QSPR
    'QSARModel',
    'DescriptorCalculator',
    'ADMETPredictor',
    'ActivityCliff',
    'ModelValidator',
    
    # Synthesis planning
    'ReactionPlanner',
    'RetrosyntheticAnalyzer',
    'RouteOptimizer',
    'ReactionDatabase',
    
    # Virtual screening
    'VirtualScreener',
    'CompoundLibrary',
    'HitIdentifier',
    'LeadOptimizer',
    'FragmentBasedDesign',
    
    # Machine learning
    'GraphNeuralNetwork',
    'MolecularTransformer',
    'GenerativeModel',
    'PropertyPredictor',
    
    # Visualization
    'MolecularViewer',
    'InteractionPlotter',
    'PharmacophoreMapper',
    'DockingVisualizer'
]