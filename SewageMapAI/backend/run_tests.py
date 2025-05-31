# filepath: e:\HackVortex\SewageMapAI\backend\run_tests.py
import os
import sys
import subprocess

def run_tests():
    """Run all tests and display results"""
    print("=" * 50)
    print("Running SewageMapAI Backend Tests")
    print("=" * 50)
    
    # Ensure we have pytest installed
    try:
        import pytest
    except ImportError:
        print("pytest not found. Installing pytest...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Run tests with coverage report
    print("\nRunning tests with coverage report...\n")
    
    subprocess.call([
        sys.executable, 
        "-m", "pytest",
        "-v",
        "--cov=.",
        "--cov-report=term",
        "tests/"
    ])
    
    print("\nTest run complete.")

if __name__ == "__main__":
    run_tests()
