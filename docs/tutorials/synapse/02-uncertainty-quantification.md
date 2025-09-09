# Advanced Uncertainty Quantification in Synapse

Uncertainty is fundamental to science. Synapse Language provides the most advanced uncertainty quantification system available, enabling scientists to work with uncertain data as naturally as with precise values.

## Table of Contents

1. [Understanding Uncertainty in Science](#understanding-uncertainty)
2. [Creating Uncertain Values](#creating-uncertain-values)
3. [Uncertainty Propagation Methods](#propagation-methods)
4. [Correlated Uncertainties](#correlated-uncertainties)
5. [Bayesian Updates](#bayesian-updates)
6. [Real-World Examples](#real-world-examples)

## Understanding Uncertainty

Every measurement in science has uncertainty. Traditional programming languages treat this as an afterthought, but Synapse makes uncertainty a first-class citizen:

```synapse
# Traditional approach (error-prone)
temperature = 298.15
temperature_error = 2.0
# Easy to forget to propagate errors!

# Synapse approach (natural)
uncertain temperature = 298.15 ± 2.0
# Uncertainty automatically propagated through all calculations
```

## Creating Uncertain Values

Synapse supports multiple uncertainty distributions:

```synapse
# Gaussian/Normal uncertainty (most common)
uncertain mass = 5.67 ± 0.03  # kg

# Uniform uncertainty (bounded measurements)
uncertain length = uniform(2.45, 2.55)  # meters, uniform between bounds

# Triangular uncertainty (most likely value with bounds)
uncertain voltage = triangular(11.8, 12.0, 12.3)  # most likely 12.0V

# Custom distribution from measurements
measurements = [12.1, 11.9, 12.0, 12.2, 11.8, 12.1]
uncertain experimental_value = from_measurements(measurements)

# Confidence intervals
uncertain pressure = 1.013 ± 0.005 @ 95%  # 95% confidence interval
```

## Uncertainty Propagation Methods

Synapse provides multiple methods for propagating uncertainty:

### 1. Automatic Propagation (Default)

```synapse
uncertain x = 10.0 ± 0.5
uncertain y = 5.0 ± 0.2

# All operations automatically propagate uncertainty
z = x * y + sqrt(x)  # Result: 55.16 ± 3.12
w = sin(x/y) * exp(y)  # Complex functions work seamlessly
```

### 2. Monte Carlo Propagation

For complex, non-linear functions:

```synapse
uncertain temperature = 300.0 ± 10.0
uncertain activation_energy = 50000.0 ± 5000.0

# Complex Arrhenius equation
monte_carlo(samples=100000) {
    rate_constant = A * exp(-activation_energy / (R * temperature))
}

print("Reaction rate constant:", rate_constant)
```

### 3. Symbolic Differentiation

For analytical uncertainty propagation:

```synapse
uncertain radius = 2.5 ± 0.1
uncertain height = 5.0 ± 0.2

# Symbolic propagation for cylinder volume
symbolic_propagation {
    volume = π * radius^2 * height
}

# Synapse automatically computes partial derivatives
print("Volume:", volume)
print("Sensitivity to radius:", volume.sensitivity(radius))
print("Sensitivity to height:", volume.sensitivity(height))
```

### 4. Bayesian Propagation

For updating beliefs with new evidence:

```synapse
# Prior belief about a physical constant
uncertain gravitational_constant = 6.674e-11 ± 0.015e-11

# New experimental measurements
new_measurements = [6.671e-11, 6.676e-11, 6.673e-11, 6.675e-11]

# Bayesian update
bayesian_update(gravitational_constant, new_measurements) {
    # Synapse computes optimal posterior distribution
    updated_g = combine_evidence(prior=gravitational_constant, 
                                likelihood=new_measurements)
}

print("Updated G:", updated_g)
print("Uncertainty reduction:", gravitational_constant.uncertainty / updated_g.uncertainty)
```

## Correlated Uncertainties

Real measurements often have correlations. Synapse handles this correctly:

```synapse
# Define correlated measurements
uncertain voltage_1 = 12.0 ± 0.1
uncertain voltage_2 = 11.8 ± 0.1

# Set correlation (same systematic error affects both)
correlate(voltage_1, voltage_2, correlation=0.8)

# Calculations account for correlation
voltage_diff = voltage_1 - voltage_2  # Uncertainty is smaller due to correlation
voltage_sum = voltage_1 + voltage_2   # Uncertainty is larger due to correlation

print("Voltage difference:", voltage_diff)  # ≈ 0.2 ± 0.06 (not ± 0.14!)
print("Voltage sum:", voltage_sum)          # ≈ 23.8 ± 0.18 (not ± 0.14!)
```

### Advanced Correlation Example

```synapse
# Multiple correlated measurements from same instrument
instrument_measurements {
    uncertain temp_1 = 25.1 ± 0.2
    uncertain temp_2 = 25.3 ± 0.2  
    uncertain temp_3 = 24.9 ± 0.2
    
    # Common systematic error from calibration
    set_systematic_correlation(0.7)
}

# Average accounts for correlation correctly
average_temp = mean(temp_1, temp_2, temp_3)
print("Average temperature:", average_temp)  # Proper uncertainty propagation
```

## Advanced Uncertainty Operations

### Confidence Intervals and Percentiles

```synapse
uncertain measurement = 42.3 ± 1.2

print("68% confidence interval:", measurement.interval(0.68))
print("95% confidence interval:", measurement.interval(0.95))
print("99% confidence interval:", measurement.interval(0.99))

print("10th percentile:", measurement.percentile(0.10))
print("90th percentile:", measurement.percentile(0.90))
```

### Sensitivity Analysis

```synapse
uncertain force = 100.0 ± 5.0      # N
uncertain area = 0.01 ± 0.0002     # m²

pressure = force / area

# Analyze which input contributes most to output uncertainty
sensitivity_analysis(pressure) {
    print("Force contribution:", contribution(force))      # ~90%
    print("Area contribution:", contribution(area))        # ~10%
}
```

### Measurement Combination

```synapse
# Multiple measurements of same quantity
measurements = [
    5.67 ± 0.03,
    5.71 ± 0.05,
    5.69 ± 0.02,
    5.68 ± 0.04
]

# Optimal weighted combination
combined = optimal_combination(measurements)
print("Combined result:", combined)  # Best estimate with minimal uncertainty

# Different combination methods
print("Simple average:", simple_average(measurements))
print("Weighted average:", weighted_average(measurements))
print("Robust average:", robust_average(measurements))  # Outlier-resistant
```

## Real-World Examples

### Example 1: Experimental Physics

```synapse
# Measuring gravitational acceleration
uncertain height = 1.523 ± 0.002      # m
uncertain time_1 = 0.556 ± 0.003       # s
uncertain time_2 = 0.554 ± 0.003       # s
uncertain time_3 = 0.558 ± 0.003       # s

# Average fall time
average_time = mean(time_1, time_2, time_3)

# Calculate g with uncertainty
g_measured = 2 * height / (average_time^2)

print("Measured g:", g_measured)
print("Difference from standard:", g_measured - 9.81)
print("Relative uncertainty:", g_measured.relative_uncertainty)

# Compare with accepted value
theoretical_g = 9.81 ± 0.01
compatibility = statistical_compatibility(g_measured, theoretical_g)
print("Statistical compatibility:", compatibility)
```

### Example 2: Chemical Analysis

```synapse
# Spectroscopic analysis with calibration uncertainty
uncertain calibration_slope = 0.0234 ± 0.0003
uncertain calibration_intercept = 0.012 ± 0.005
uncertain absorbance = 0.456 ± 0.008

# Beer's law calculation
concentration = (absorbance - calibration_intercept) / calibration_slope

print("Concentration:", concentration)  # Includes all uncertainty sources

# Limit of detection analysis
signal_noise_ratio = concentration / concentration.uncertainty
print("Signal-to-noise ratio:", signal_noise_ratio)

if signal_noise_ratio > 3.0:
    print("Above detection limit ✓")
else:
    print("Below detection limit ✗")
```

### Example 3: Climate Data Analysis

```synapse
# Temperature measurements with various uncertainties
uncertain surface_temp = 14.2 ± 0.3     # °C
uncertain satellite_temp = 13.8 ± 0.5   # °C
uncertain radiosonde_temp = 14.0 ± 0.4  # °C

# Model prediction
uncertain model_prediction = 14.1 ± 0.2

# Data assimilation - combine all sources
assimilated_temp = data_assimilation {
    observations: [surface_temp, satellite_temp, radiosonde_temp]
    model: model_prediction
    weights: "optimal"  # Inverse variance weighting
}

print("Best temperature estimate:", assimilated_temp)

# Climate trend analysis
years = [2020, 2021, 2022, 2023]
temps = [13.8±0.2, 14.1±0.3, 14.3±0.2, 14.5±0.3]

trend = linear_regression(years, temps)
print("Warming trend:", trend.slope, "°C/year")
print("Trend significance:", trend.p_value)
```

## Best Practices

### 1. Always Include Uncertainty
```synapse
# Bad: Ignoring uncertainty
temperature = 298.15
result = calculate_rate_constant(temperature)

# Good: Including uncertainty
uncertain temperature = 298.15 ± 2.0
uncertain result = calculate_rate_constant(temperature)
```

### 2. Validate Uncertainty Propagation
```synapse
uncertain x = 10.0 ± 0.1
result = complex_calculation(x)

# Validate with Monte Carlo
monte_carlo_result = monte_carlo(samples=10000) {
    complex_calculation(x)
}

print("Analytical result:", result)
print("Monte Carlo result:", monte_carlo_result)
print("Agreement:", statistical_agreement(result, monte_carlo_result))
```

### 3. Document Uncertainty Sources
```synapse
uncertain mass = 5.67 ± 0.03 {
    systematic: 0.02,    # Balance calibration
    statistical: 0.02,   # Measurement repeatability
    source: "analytical_balance_model_XYZ"
}
```

### 4. Check for Bias
```synapse
measurements = [12.1, 11.9, 12.0, 12.2, 11.8]
reference_value = 12.05

bias_analysis(measurements, reference_value) {
    print("Mean bias:", calculate_bias())
    print("Bias significance:", bias_t_test())
    print("Systematic component:", estimate_systematic_error())
}
```

## Next Steps

- **[Tutorial 3: Parallel Computing](03-parallel-computing.md)** - Use parallel processing to speed up uncertainty calculations
- **[Tutorial 5: Machine Learning](05-machine-learning.md)** - Combine uncertainty with ML models
- **[Real-World Examples](../examples/chemistry)** - See uncertainty quantification in action

## Further Reading

- [JCGM 100:2008 - Guide to Expression of Uncertainty in Measurement](https://www.bipm.org/en/publications/guides)
- [Taylor & Kuyatt - Guidelines for Evaluating and Expressing Uncertainty](https://physics.nist.gov/Pubs/guidelines/TN1297/tn1297s.pdf)
- [Numerical Recipes - Monte Carlo Methods](http://numerical.recipes/)