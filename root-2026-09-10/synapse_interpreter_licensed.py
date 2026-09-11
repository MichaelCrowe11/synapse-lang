#!/usr/bin/env python3
"""
Licensed version of Synapse Interpreter
Enforces license restrictions and feature flags
"""


from synapse_interpreter_enhanced import *
from synapse_licensing import (
    FeatureFlag,
    LicenseError,
    get_license_manager,
    require_feature,
)


class LicensedSynapseInterpreter(SynapseInterpreterEnhanced):
    """License-aware Synapse interpreter"""

    def __init__(self):
        super().__init__()
        self.license_manager = get_license_manager()
        self._show_license_banner()
        self._apply_license_restrictions()

    def _show_license_banner(self):
        """Show license information on startup"""
        info = self.license_manager.get_license_info()
        print(f"Synapse-Lang {info['type'].upper()} Edition v1.0.0")
        print(f"Licensed to: {info['owner']}")
        if info["expires"] != "Never":
            print(f"License expires: {info['expires']}")
        print("-" * 50)

    def _apply_license_restrictions(self):
        """Apply license-based restrictions"""
        self.license_manager.get_license_info()

        # Limit parallel execution based on license
        if not self.license_manager.has_feature(FeatureFlag.UNLIMITED_CORES):
            max_cores = self.license_manager.current_license.max_cores
            self.executor = ThreadPoolExecutor(max_workers=max_cores)

        # Disable advanced features for community edition
        if not self.license_manager.has_feature(FeatureFlag.SYMBOLIC_ADVANCED):
            self._limit_symbolic_features()

        if not self.license_manager.has_feature(FeatureFlag.GPU_ACCELERATION):
            self._disable_gpu()

    def _limit_symbolic_features(self):
        """Limit symbolic math features for community edition"""
        # Override symbolic engine methods
        self.symbolic_engine.laplace_transform = lambda *args, **kwargs: self._require_pro_feature("Laplace transform")

        self.symbolic_engine.fourier_transform = lambda *args, **kwargs: self._require_pro_feature("Fourier transform")

    def _disable_gpu(self):
        """Disable GPU acceleration"""
        # Would disable CuPy/CUDA features here
        pass

    def _require_pro_feature(self, feature_name: str):
        """Helper to require professional features"""
        raise LicenseError(f"{feature_name} requires Professional or Enterprise license")

    @require_feature(FeatureFlag.ADVANCED_PARALLEL)
    def visit_ParallelNode(self, node: ParallelNode) -> Dict[str, Any]:
        """Execute parallel branches (requires appropriate license)"""
        # Check core limits
        if node.factor and isinstance(node.factor, int):
            self.license_manager.check_limits(cores=node.factor)

        return super().visit_ParallelNode(node)

    @require_feature(FeatureFlag.PIPELINE_ADVANCED)
    def visit_PipelineNode(self, node: PipelineNode) -> Dict[str, Any]:
        """Execute pipeline (requires appropriate license for advanced features)"""
        # Community edition limited to sequential pipelines
        if not self.license_manager.has_feature(FeatureFlag.PIPELINE_ADVANCED):
            # Force sequential execution
            for stage in node.stages:
                if stage.parallel_factor:
                    stage.parallel_factor = 1

        return super().visit_PipelineNode(node)

    @require_feature(FeatureFlag.QUANTUM_NET)
    def visit_QuantumNetNode(self, node) -> Any:
        """Quantum networking (Enterprise only)"""
        return super().visit_QuantumNetNode(node)

    def visit_TensorDeclarationNode(self, node: TensorDeclarationNode) -> SynapseTensor:
        """Execute tensor declaration with size limits"""
        # Calculate tensor size
        dims = []
        for dim_expr in node.dimensions:
            dim = self.visit(dim_expr)
            dims.append(int(dim) if isinstance(dim, (int, float)) else dim)

        total_elements = 1
        for d in dims:
            total_elements *= d

        # Community edition tensor size limit
        if not self.license_manager.has_feature(FeatureFlag.UNLIMITED_CORES):
            MAX_TENSOR_SIZE = 10_000_000  # 10M elements for community
            if total_elements > MAX_TENSOR_SIZE:
                raise LicenseError(f"Tensor size {total_elements} exceeds community edition limit of {MAX_TENSOR_SIZE}")

        return super().visit_TensorDeclarationNode(node)

    def execute(self, source: str) -> Any:
        """Execute with telemetry (Enterprise only)"""
        # Track usage for enterprise licenses
        if self.license_manager.has_feature(FeatureFlag.TELEMETRY_ANALYTICS):
            self._track_usage(source)

        # Check for commercial use restriction
        if self._detect_commercial_use(source):
            if not self.license_manager.has_feature(FeatureFlag.COMMERCIAL_USE):
                raise LicenseError("Commercial use requires Professional or Enterprise license")

        return super().execute(source)

    def _track_usage(self, source: str):
        """Track usage telemetry (Enterprise feature)"""
        # Would send telemetry to server
        pass

    def _detect_commercial_use(self, source: str) -> bool:
        """Detect potential commercial use patterns"""
        commercial_indicators = [
            "production",
            "customer",
            "client",
            "revenue",
            "profit",
            "business",
            "enterprise",
            "commercial",
        ]

        source_lower = source.lower()
        for indicator in commercial_indicators:
            if indicator in source_lower:
                return True

        return False

    def show_license_features(self):
        """Show available features based on license"""
        print("\n" + "="*60)
        print("AVAILABLE FEATURES")
        print("="*60)

        all_features = [
            (FeatureFlag.BASIC_INTERPRETER, "Basic Interpreter"),
            (FeatureFlag.BASIC_PARALLEL, "Basic Parallel (4 cores)"),
            (FeatureFlag.ADVANCED_PARALLEL, "Advanced Parallel"),
            (FeatureFlag.UNLIMITED_CORES, "Unlimited CPU Cores"),
            (FeatureFlag.GPU_ACCELERATION, "GPU Acceleration"),
            (FeatureFlag.SYMBOLIC_ADVANCED, "Advanced Symbolic Math"),
            (FeatureFlag.PIPELINE_ADVANCED, "Advanced Pipelines"),
            (FeatureFlag.QUANTUM_NET, "Quantum Networking"),
            (FeatureFlag.QUBIT_FLOW_UNLIMITED, "Unlimited Qubits"),
            (FeatureFlag.CLOUD_INTEGRATION, "Cloud Integration"),
            (FeatureFlag.COMMERCIAL_USE, "Commercial Use"),
            (FeatureFlag.TELEMETRY_ANALYTICS, "Usage Analytics"),
        ]

        for feature, name in all_features:
            if self.license_manager.has_feature(feature):
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} (upgrade required)")

        print("="*60)

def main():
    """Main entry point for licensed interpreter"""
    import sys

    interpreter = LicensedSynapseInterpreter()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--license":
            interpreter.show_license_features()
        elif sys.argv[1] == "--version":
            info = interpreter.license_manager.get_license_info()
            print(f"Synapse-Lang {info['type'].upper()} Edition v1.0.0")
        else:
            # Execute file
            filename = sys.argv[1]
            try:
                with open(filename) as f:
                    source = f.read()
                result = interpreter.execute(source)
                if result:
                    interpreter.display_result(result)
            except LicenseError as e:
                print(f"\n❌ License Error: {e}")
                print("Consider upgrading your license at https://synapse-lang.com/pricing")
                sys.exit(1)
    else:
        # Run REPL
        try:
            interpreter.run_repl()
        except LicenseError as e:
            print(f"\n❌ License Error: {e}")
            print("Consider upgrading your license at https://synapse-lang.com/pricing")
            sys.exit(1)

if __name__ == "__main__":
    main()
