"""
Integration tests for documentation examples.

Validates that all examples in the documentation actually work correctly.
"""

import unittest
import sys
import os
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from synapse_lang import UncertainValue, monte_carlo, parallel_block, parameter_sweep
from synapse_lang.ml_integration import GaussianProcessUncertainty


class TestDrugDiscoveryExample(unittest.TestCase):
    """Test the drug discovery pipeline example."""
    
    def test_molecular_docking_uncertainty(self):
        """Test molecular docking with uncertainty."""
        # Simulate molecular docking scores with uncertainty
        binding_affinities = [
            UncertainValue(-8.5, 0.3),  # kcal/mol
            UncertainValue(-7.2, 0.4),
            UncertainValue(-9.1, 0.2),
            UncertainValue(-6.8, 0.5)
        ]
        
        # Filter high-affinity compounds
        threshold = UncertainValue(-8.0, 0.1)
        
        promising_compounds = []
        for affinity in binding_affinities:
            # Check if significantly better than threshold
            if affinity.value < threshold.value - 2 * affinity.uncertainty:
                promising_compounds.append(affinity)
                
        # Should identify the -9.1 compound as promising
        self.assertEqual(len(promising_compounds), 1)
        self.assertAlmostEqual(promising_compounds[0].value, -9.1, places=1)
        
    def test_parallel_drug_screening(self):
        """Test parallel screening of compound library."""
        def score_compound(compound_id):
            """Simulate docking score calculation."""
            np.random.seed(compound_id)
            base_score = -6.0 - np.random.exponential(1.0)  # Negative is better
            uncertainty = 0.2 + np.random.random() * 0.3
            return UncertainValue(base_score, uncertainty)
            
        # Screen compound library in parallel
        compound_ids = list(range(100))
        
        docking_scores = parallel_block(
            function=score_compound,
            inputs=compound_ids
        )
        
        # Find top compounds
        top_compounds = sorted(docking_scores, key=lambda x: x.value)[:10]
        
        # Verify we have 10 compounds
        self.assertEqual(len(top_compounds), 10)
        
        # Top compounds should have good scores
        for compound in top_compounds:
            self.assertLess(compound.value, -6.0)
            
    def test_qsar_model_uncertainty(self):
        """Test QSAR model with uncertainty quantification."""
        # Simulate molecular descriptors
        n_compounds = 50
        n_features = 10
        
        X = np.random.randn(n_compounds, n_features)
        
        # True relationship with noise
        true_weights = np.random.randn(n_features)
        y_true = X @ true_weights
        y_observed = y_true + np.random.normal(0, 0.5, n_compounds)
        
        # Add measurement uncertainty
        y_uncertain = [
            UncertainValue(y_observed[i], 0.1 + 0.4 * np.random.random())
            for i in range(n_compounds)
        ]
        
        # Fit Gaussian Process with uncertainty
        gp_model = GaussianProcessUncertainty()
        gp_model.fit(X, y_uncertain)
        
        # Predict on new compounds
        X_test = np.random.randn(10, n_features)
        predictions = gp_model.predict(X_test)
        
        # Check predictions have uncertainty
        for pred in predictions:
            self.assertIsInstance(pred, UncertainValue)
            self.assertGreater(pred.uncertainty, 0)


class TestFinancialRiskExample(unittest.TestCase):
    """Test the financial risk analysis example."""
    
    def test_portfolio_value_uncertainty(self):
        """Test portfolio value calculation with uncertainty."""
        portfolio = {
            "AAPL": {
                "shares": 100,
                "price": UncertainValue(180.50, 2.15)
            },
            "GOOGL": {
                "shares": 50,
                "price": UncertainValue(2750.25, 15.80)
            },
            "BTC": {
                "shares": 0.5,
                "price": UncertainValue(45250, 1250)
            }
        }
        
        # Calculate total portfolio value
        total_value = UncertainValue(0, 0)
        for asset, details in portfolio.items():
            position_value = details["shares"] * details["price"]
            total_value = total_value + position_value
            
        # Check total value is reasonable
        self.assertGreater(total_value.value, 100000)
        self.assertLess(total_value.value, 500000)
        
        # Check uncertainty propagated
        self.assertGreater(total_value.uncertainty, 0)
        
    def test_var_calculation(self):
        """Test Value at Risk calculation."""
        # Simulate portfolio returns
        returns = np.random.normal(0.001, 0.02, 10000)  # 0.1% mean, 2% std
        
        # Calculate VaR at 95% confidence
        var_95 = np.percentile(returns, 5)
        
        # Calculate CVaR (Conditional VaR)
        losses = returns[returns <= var_95]
        cvar_95 = np.mean(losses)
        
        # VaR should be negative (loss)
        self.assertLess(var_95, 0)
        
        # CVaR should be worse than VaR
        self.assertLess(cvar_95, var_95)
        
    def test_monte_carlo_risk_simulation(self):
        """Test Monte Carlo risk simulation with uncertainty."""
        # Market parameters with uncertainty
        volatility = UncertainValue(0.20, 0.02)  # 20% ± 2%
        drift = UncertainValue(0.08, 0.01)       # 8% ± 1%
        
        initial_price = 100.0
        time_horizon = 1.0  # 1 year
        
        def simulate_price_path(vol, mu):
            """Geometric Brownian Motion."""
            dt = 1/252  # Daily steps
            n_steps = int(time_horizon / dt)
            
            returns = np.random.normal(
                mu * dt,
                vol * np.sqrt(dt),
                n_steps
            )
            
            price_path = initial_price * np.exp(np.cumsum(returns))
            return price_path[-1]
            
        # Run Monte Carlo
        final_prices = monte_carlo(
            function=simulate_price_path,
            inputs={'vol': volatility, 'mu': drift},
            samples=1000
        )
        
        # Check result has uncertainty from market parameters
        self.assertIsInstance(final_prices, UncertainValue)
        self.assertGreater(final_prices.uncertainty, 0)
        
        # Mean should be close to expected (e^(drift * time))
        expected = initial_price * np.exp(drift.value * time_horizon)
        self.assertAlmostEqual(final_prices.value, expected, delta=10)


class TestClimateModelingExample(unittest.TestCase):
    """Test the climate modeling ensemble example."""
    
    def test_emission_scenario_uncertainty(self):
        """Test emission scenarios with uncertainty."""
        scenarios = [
            {
                "name": "RCP2.6",
                "co2_2050": UncertainValue(420, 15),
                "co2_2100": UncertainValue(450, 25),
                "temperature": UncertainValue(1.5, 0.2)
            },
            {
                "name": "RCP4.5", 
                "co2_2050": UncertainValue(485, 20),
                "co2_2100": UncertainValue(540, 30),
                "temperature": UncertainValue(2.4, 0.3)
            },
            {
                "name": "RCP8.5",
                "co2_2050": UncertainValue(570, 25),
                "co2_2100": UncertainValue(850, 50),
                "temperature": UncertainValue(4.3, 0.5)
            }
        ]
        
        # Check ordering of scenarios
        for i in range(len(scenarios) - 1):
            self.assertLess(
                scenarios[i]["co2_2100"].value,
                scenarios[i+1]["co2_2100"].value
            )
            self.assertLess(
                scenarios[i]["temperature"].value,
                scenarios[i+1]["temperature"].value
            )
            
    def test_model_ensemble_statistics(self):
        """Test climate model ensemble statistics."""
        # Simulate ensemble of climate models
        models = [
            {"name": "Model1", "sensitivity": UncertainValue(3.2, 0.4)},
            {"name": "Model2", "sensitivity": UncertainValue(2.9, 0.3)},
            {"name": "Model3", "sensitivity": UncertainValue(3.5, 0.5)},
            {"name": "Model4", "sensitivity": UncertainValue(4.1, 0.6)},
            {"name": "Model5", "sensitivity": UncertainValue(3.0, 0.35)}
        ]
        
        # Calculate ensemble mean
        sensitivities = [m["sensitivity"] for m in models]
        
        # Simple mean
        mean_sensitivity = sum(s.value for s in sensitivities) / len(sensitivities)
        
        # Uncertainty from spread
        model_spread = np.std([s.value for s in sensitivities])
        
        # Combined uncertainty
        param_uncertainty = np.mean([s.uncertainty for s in sensitivities])
        total_uncertainty = np.sqrt(model_spread**2 + param_uncertainty**2)
        
        ensemble_sensitivity = UncertainValue(mean_sensitivity, total_uncertainty)
        
        # Check ensemble statistics
        self.assertAlmostEqual(ensemble_sensitivity.value, 3.34, places=1)
        self.assertGreater(ensemble_sensitivity.uncertainty, 0.4)
        
    def test_parallel_climate_simulations(self):
        """Test parallel climate ensemble simulations."""
        def run_climate_model(model_id, scenario_id, realization):
            """Simulate a single climate model run."""
            np.random.seed(model_id * 100 + scenario_id * 10 + realization)
            
            # Simple temperature projection
            base_temp = 15.0
            scenario_warming = scenario_id * 1.5  # Simplified
            model_bias = (model_id - 2) * 0.3
            natural_variability = np.random.normal(0, 0.5)
            
            return base_temp + scenario_warming + model_bias + natural_variability
            
        # Define ensemble parameters
        n_models = 5
        n_scenarios = 3
        n_realizations = 10
        
        # Generate all combinations
        simulations = []
        for model in range(n_models):
            for scenario in range(n_scenarios):
                for realization in range(n_realizations):
                    simulations.append((model, scenario, realization))
                    
        # Run ensemble in parallel
        results = parallel_block(
            function=lambda params: run_climate_model(*params),
            inputs=simulations
        )
        
        # Should have all results
        self.assertEqual(len(results), n_models * n_scenarios * n_realizations)
        
        # Reshape and analyze
        results_array = np.array(results).reshape(n_models, n_scenarios, n_realizations)
        
        # Higher scenarios should have higher temperatures
        scenario_means = np.mean(results_array, axis=(0, 2))
        for i in range(n_scenarios - 1):
            self.assertLess(scenario_means[i], scenario_means[i+1])


class TestQuantumMLExample(unittest.TestCase):
    """Test the quantum machine learning example integration."""
    
    def test_quantum_feature_encoding(self):
        """Test encoding classical features for quantum circuits."""
        # Classical features with uncertainty
        features = [
            UncertainValue(0.5, 0.05),
            UncertainValue(0.3, 0.03),
            UncertainValue(0.7, 0.07),
            UncertainValue(0.2, 0.02)
        ]
        
        # Normalize features for quantum encoding (angles)
        normalized = []
        for f in features:
            # Map to [0, 2π]
            angle = f.value * 2 * np.pi
            angle_uncertainty = f.uncertainty * 2 * np.pi
            normalized.append(UncertainValue(angle, angle_uncertainty))
            
        # Check normalization
        for n in normalized:
            self.assertGreaterEqual(n.value, 0)
            self.assertLessEqual(n.value, 2 * np.pi)
            
    def test_hybrid_training_loop(self):
        """Test hybrid classical-quantum training."""
        # Simulate quantum circuit predictions
        def quantum_predict(params, features):
            """Mock quantum circuit execution."""
            # Simple linear combination for testing
            prediction = sum(p * f for p, f in zip(params, features))
            # Add shot noise
            shot_noise = np.random.normal(0, 0.01)
            return prediction + shot_noise
            
        # Training data
        n_samples = 20
        n_features = 4
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 2, n_samples)
        
        # Initialize parameters
        params = np.random.randn(n_features) * 0.1
        
        # Training loop
        learning_rate = 0.01
        n_epochs = 10
        
        for epoch in range(n_epochs):
            total_loss = 0
            
            for i in range(n_samples):
                # Forward pass
                pred = quantum_predict(params, X[i])
                
                # Binary classification loss
                pred_prob = 1 / (1 + np.exp(-pred))  # Sigmoid
                loss = -y[i] * np.log(pred_prob + 1e-10) - (1-y[i]) * np.log(1-pred_prob + 1e-10)
                total_loss += loss
                
                # Gradient estimation (parameter shift rule simplified)
                gradients = []
                for j in range(n_features):
                    params_plus = params.copy()
                    params_plus[j] += np.pi/4
                    pred_plus = quantum_predict(params_plus, X[i])
                    
                    params_minus = params.copy()
                    params_minus[j] -= np.pi/4
                    pred_minus = quantum_predict(params_minus, X[i])
                    
                    grad = (pred_plus - pred_minus) / 2
                    gradients.append(grad)
                    
                # Update parameters
                params -= learning_rate * np.array(gradients)
                
        # Training should reduce loss
        self.assertLess(total_loss / n_samples, 1.0)


class TestParallelWorkflows(unittest.TestCase):
    """Test complex parallel scientific workflows."""
    
    def test_nested_parallel_sweep(self):
        """Test nested parameter sweeps with uncertainty."""
        def inner_calculation(x, y, uncertainty_level):
            """Inner loop calculation."""
            result = x * np.exp(-y)
            uncertainty = result * uncertainty_level
            return UncertainValue(result, uncertainty)
            
        def outer_calculation(temperature, pressure):
            """Outer loop with inner parameter sweep."""
            # Each outer parameter triggers inner sweep
            x_values = [1.0, 2.0, 3.0]
            y_values = [0.1, 0.2]
            
            inner_results = parameter_sweep(
                function=lambda x, y: inner_calculation(x, y, 0.05),
                parameters={'x': x_values, 'y': y_values}
            )
            
            # Aggregate inner results (parameter_sweep returns dict with tuple keys)
            mean_result = np.mean([r.value if hasattr(r, 'value') else r 
                                   for r in inner_results.values()])
            
            # Apply outer parameters
            final = mean_result * temperature / pressure
            return final
            
        # Outer sweep
        temperatures = [273, 298, 323]
        pressures = [1.0, 1.5]
        
        outer_results = parameter_sweep(
            function=outer_calculation,
            parameters={
                'temperature': temperatures,
                'pressure': pressures
            }
        )
        
        # Check all combinations computed
        self.assertEqual(len(outer_results), 6)
        
    def test_adaptive_refinement(self):
        """Test adaptive parameter refinement based on uncertainty."""
        def uncertain_function(x):
            """Function with varying uncertainty."""
            value = np.sin(x) * np.exp(-x/10)
            # Higher uncertainty near x=5
            uncertainty = 0.01 + 0.1 * np.exp(-((x-5)**2)/2)
            return UncertainValue(value, uncertainty)
            
        # Initial coarse sampling
        x_coarse = np.linspace(0, 10, 11)
        
        results_coarse = [uncertain_function(x) for x in x_coarse]
        
        # Find regions with high uncertainty
        high_uncertainty_regions = []
        for i, result in enumerate(results_coarse):
            if result.uncertainty > 0.05:
                if i > 0 and i < len(x_coarse) - 1:
                    high_uncertainty_regions.append((x_coarse[i-1], x_coarse[i+1]))
                    
        # Refine in high uncertainty regions
        x_refined = []
        for region in high_uncertainty_regions:
            x_refined.extend(np.linspace(region[0], region[1], 5))
            
        results_refined = [uncertain_function(x) for x in x_refined]
        
        # Should have refined near x=5
        refined_near_5 = [x for x in x_refined if 4 < x < 6]
        self.assertGreater(len(refined_near_5), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)