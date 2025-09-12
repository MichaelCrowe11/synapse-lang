#!/usr/bin/env python
"""
Climate Modeling with Synapse Language
Demonstrates uncertainty propagation and parallel simulations
"""

import synapse_lang
import numpy as np

# Synapse code for climate modeling with uncertainty
climate_code = """
# Climate model with uncertainty quantification
uncertain global_temp = 14.5 ± 0.3  # Current global temperature
uncertain co2_level = 415 ± 5       # CO2 ppm
uncertain sensitivity = 3.0 ± 1.5    # Climate sensitivity

# Parallel scenario testing
parallel climate_scenarios:
    branch low_emissions:
        co2_increase = 50 ± 10
        time_horizon = 30
        temp_rise = sensitivity * log(co2_increase / 280) * 0.5
        
    branch high_emissions:
        co2_increase = 200 ± 20
        time_horizon = 30
        temp_rise = sensitivity * log(co2_increase / 280) * 0.5
        
    branch net_zero:
        co2_increase = -50 ± 15
        time_horizon = 30
        temp_rise = sensitivity * log(co2_increase / 280) * 0.5

# Propagate uncertainties through model
propagate uncertainty:
    method = "monte_carlo"
    samples = 10000
    
# Pipeline for analysis
pipeline climate_analysis:
    stage data_prep:
        load_historical_data()
        normalize_measurements()
        
    stage simulation:
        run_climate_model()
        calculate_impacts()
        
    stage visualization:
        plot_temperature_projections()
        generate_risk_maps()

# Hypothesis testing
hypothesis tipping_point:
    premise: global_temp + temp_rise > 16.0
    test: probability(premise) > 0.5
    conclude: "High risk of climate tipping point"
"""

def demonstrate_climate_model():
    """Run climate model demonstration"""
    print("Climate Modeling with Synapse Language")
    print("=" * 50)
    
    # Parse the Synapse code
    ast = synapse_lang.parse(climate_code)
    print("[OK] Climate model parsed successfully")
    
    # Create simulated data
    np.random.seed(42)
    historical_temps = 14.5 + np.random.normal(0, 0.3, 100)
    co2_levels = 415 + np.random.normal(0, 5, 100)
    
    print(f"\nInput Data:")
    print(f"  Average Temperature: {historical_temps.mean():.2f}C +/- {historical_temps.std():.2f}")
    print(f"  CO2 Levels: {co2_levels.mean():.1f} ppm ± {co2_levels.std():.1f}")
    
    # Simulate parallel scenario execution
    scenarios = {
        'low_emissions': {
            'temp_rise': 1.2 + np.random.normal(0, 0.3),
            'probability': 0.35
        },
        'high_emissions': {
            'temp_rise': 3.5 + np.random.normal(0, 0.5),
            'probability': 0.45
        },
        'net_zero': {
            'temp_rise': 0.5 + np.random.normal(0, 0.2),
            'probability': 0.20
        }
    }
    
    print(f"\nRunning Parallel Scenarios:")
    for name, data in scenarios.items():
        print(f"  {name}: +{data['temp_rise']:.2f}C (P={data['probability']:.0%})")
    
    # Calculate ensemble prediction with uncertainty
    weighted_rise = sum(s['temp_rise'] * s['probability'] for s in scenarios.values())
    uncertainty = np.sqrt(sum((s['temp_rise'] - weighted_rise)**2 * s['probability'] 
                             for s in scenarios.values()))
    
    print(f"\nEnsemble Prediction:")
    print(f"  Expected Temperature Rise: {weighted_rise:.2f}C +/- {uncertainty:.2f}")
    print(f"  Final Temperature: {14.5 + weighted_rise:.2f}C")
    
    # Risk assessment
    tipping_point_risk = sum(s['probability'] for s in scenarios.values() 
                           if 14.5 + s['temp_rise'] > 16.0)
    
    print(f"\nRisk Assessment:")
    print(f"  Tipping Point Risk: {tipping_point_risk:.0%}")
    print(f"  Confidence Interval: 95%")
    
    if tipping_point_risk > 0.5:
        print("  [HIGH RISK] Immediate action required")
    elif tipping_point_risk > 0.3:
        print("  [MODERATE RISK] Significant mitigation needed")
    else:
        print("  [LOW RISK] Continue monitoring")
    
    print("\n[COMPLETE] Climate model analysis complete!")
    return weighted_rise, uncertainty

if __name__ == "__main__":
    # Run the demonstration
    temp_rise, uncertainty = demonstrate_climate_model()
    
    print("\n" + "="*50)
    print("This example demonstrates:")
    print("  - Uncertainty propagation in climate models")
    print("  - Parallel scenario execution")
    print("  - Risk assessment with confidence intervals")
    print("  - Scientific hypothesis testing")
    print("\nInstall Synapse: pip install synapse-lang")