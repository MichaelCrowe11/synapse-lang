#!/usr/bin/env python3
"""
Test and demonstrate the licensing system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from synapse_licensing import (
    LicenseManager,
    LicenseType,
    FeatureFlag,
    get_license_manager
)

def test_licensing_system():
    """Test the licensing system"""
    print("="*60)
    print("SYNAPSE-LANG LICENSING SYSTEM DEMO")
    print("="*60)
    
    lm = get_license_manager()
    
    # Show current license (defaults to community)
    print("\n1. Current License Status:")
    print("-"*40)
    info = lm.get_license_info()
    print(f"Type: {info['type']}")
    print(f"Max Cores: {info['max_cores']}")
    print(f"Max Qubits: {info['max_qubits']}")
    
    # Generate different license types
    print("\n2. Generated License Keys:")
    print("-"*40)
    
    for license_type in [LicenseType.COMMUNITY, LicenseType.PROFESSIONAL, 
                         LicenseType.ENTERPRISE, LicenseType.ACADEMIC, LicenseType.TRIAL]:
        key = lm.generate_license_key(license_type, seed=license_type.value)
        print(f"{license_type.value.upper():12} : {key}")
    
    # Test feature checks
    print("\n3. Feature Availability (Current License):")
    print("-"*40)
    
    features_to_check = [
        (FeatureFlag.BASIC_INTERPRETER, "Basic Interpreter"),
        (FeatureFlag.ADVANCED_PARALLEL, "Advanced Parallel"),
        (FeatureFlag.GPU_ACCELERATION, "GPU Acceleration"),
        (FeatureFlag.QUANTUM_NET, "Quantum Networking"),
        (FeatureFlag.COMMERCIAL_USE, "Commercial Use"),
    ]
    
    for feature, name in features_to_check:
        has_feature = lm.has_feature(feature)
        status = "✓" if has_feature else "✗"
        print(f"  {status} {name:20} : {'Available' if has_feature else 'Requires Upgrade'}")
    
    # Simulate activating an enterprise license
    print("\n4. Simulating Enterprise License Activation:")
    print("-"*40)
    
    enterprise_key = lm.generate_license_key(LicenseType.ENTERPRISE, seed="test")
    print(f"Generated Key: {enterprise_key}")
    
    try:
        lm.activate_license(enterprise_key, "test@enterprise.com")
        print("✅ Enterprise license activated!")
        
        # Show new features
        print("\nFeatures after upgrade:")
        for feature, name in features_to_check:
            has_feature = lm.has_feature(feature)
            status = "✓" if has_feature else "✗"
            print(f"  {status} {name:20} : {'Available' if has_feature else 'Requires Upgrade'}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test license limits
    print("\n5. Testing License Limits:")
    print("-"*40)
    
    test_cases = [
        ("CPU Cores", 4, None),
        ("CPU Cores", 32, None),
        ("Qubits", None, 30),
        ("Qubits", None, 1000),
    ]
    
    for name, cores, qubits in test_cases:
        try:
            lm.check_limits(cores=cores, qubits=qubits)
            print(f"  ✓ {name:10} : {cores or qubits:4} - Within limits")
        except Exception as e:
            print(f"  ✗ {name:10} : {cores or qubits:4} - {str(e)[:40]}...")
    
    # License comparison table
    print("\n6. License Comparison Matrix:")
    print("-"*40)
    print(f"{'Feature':<30} {'COM':^5} {'PRO':^5} {'ENT':^5} {'ACA':^5}")
    print("-"*55)
    
    features = [
        ("Basic Interpreter", FeatureFlag.BASIC_INTERPRETER),
        ("Parallel (4 cores)", FeatureFlag.BASIC_PARALLEL),
        ("Advanced Parallel", FeatureFlag.ADVANCED_PARALLEL),
        ("Unlimited Cores", FeatureFlag.UNLIMITED_CORES),
        ("GPU Acceleration", FeatureFlag.GPU_ACCELERATION),
        ("Quantum Networking", FeatureFlag.QUANTUM_NET),
        ("Commercial Use", FeatureFlag.COMMERCIAL_USE),
    ]
    
    for feature_name, feature_flag in features:
        row = f"{feature_name:<30}"
        for license_type in [LicenseType.COMMUNITY, LicenseType.PROFESSIONAL, 
                            LicenseType.ENTERPRISE, LicenseType.ACADEMIC]:
            has_it = feature_flag in lm.FEATURE_SETS[license_type]
            row += f" {'✓' if has_it else '✗':^5}"
        print(row)
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_licensing_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)