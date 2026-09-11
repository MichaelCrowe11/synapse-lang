#!/usr/bin/env python3
"""
Synapse Language - Quick AI/ML Platform Demo

Quick demonstration of core platform capabilities.
"""

import os
import sys

import numpy as np

# Add platform to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.neural_network_dsl import Dense, NeuralNetwork


def main():
    print("SYNAPSE LANGUAGE - AI/ML PLATFORM QUICK DEMO")
    print("=" * 60)

    try:
        # Test 1: Neural Network DSL
        print("\n1. Neural Network DSL Test")
        print("-" * 40)

        model = NeuralNetwork("QuickTest")
        model.add(Dense(units=32, activation="relu", name="hidden"))
        model.add(Dense(units=1, activation="linear", name="output"))

        model.compile(optimizer="adam", loss="mse", learning_rate=0.01)
        model.summary()

        # Quick training
        X = np.random.randn(100, 10)
        y = np.random.randn(100, 1)

        model.fit(X, y, epochs=3, batch_size=32, verbose=1)

        # Test prediction
        predictions = model.predict(X[:5])
        print(f"Predictions shape: {predictions.shape}")

        print("[SUCCESS] Neural Network DSL working correctly")

        # Test 2: GPU Manager
        print("\n2. GPU Acceleration Test")
        print("-" * 40)

        from src.gpu_acceleration import create_gpu_manager

        gpu_manager = create_gpu_manager()
        print(f"[SUCCESS] GPU Manager initialized with {len(gpu_manager.devices)} devices")

        # Test 3: Model Server
        print("\n3. Model Deployment Test")
        print("-" * 40)

        from src.model_deployment import InferenceRequest, create_model_server

        server = create_model_server()
        server.register_model(model, "quick_test_model")

        # Test prediction
        request = InferenceRequest(
            request_id="test_001",
            model_id="quick_test_model",
            input_data=np.random.randn(1, 10)
        )

        response = server.predict(request)
        print(f"[SUCCESS] Model serving working - Processing time: {response.processing_time_ms:.2f}ms")

        # Test 4: AutoML (simplified)
        print("\n4. AutoML Framework Test")
        print("-" * 40)

        from src.automl_optimizer import HyperparameterRange, HyperparameterSpace

        space = HyperparameterSpace()
        space.add_parameter(HyperparameterRange("learning_rate", "float", 0.001, 0.1))
        space.add_parameter(HyperparameterRange("units", "int", 16, 64))

        # Test configuration sampling
        config = space.sample_configuration()
        print(f"[SUCCESS] AutoML framework working - Sample config: {config}")

        print("\n" + "=" * 60)
        print("QUICK DEMO COMPLETE - ALL SYSTEMS OPERATIONAL!")
        print("=" * 60)
        print("\n[SUCCESS] Neural Network DSL")
        print("[SUCCESS] GPU Acceleration Framework")
        print("[SUCCESS] Model Deployment & Serving")
        print("[SUCCESS] AutoML Optimization")
        print("\nThe Synapse Language AI/ML platform is ready!")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
