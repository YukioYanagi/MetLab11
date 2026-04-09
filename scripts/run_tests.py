#!/usr/bin/env python3
"""
Test runner script for the multi-language microservices application.
Runs unit tests for Python, Go, and Rust applications.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=shell, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        return None

def run_python_tests(project_root):
    """Run Python unit tests"""
    print("\n" + "="*50)
    print("Running Python Tests")
    print("="*50)
    
    python_app_dir = project_root / "python-app"
    
    if not python_app_dir.exists():
        print("ERROR: python-app directory not found")
        return False
    
    # Install dependencies
    print("Installing Python dependencies...")
    result = run_command("pip install -r requirements.txt", cwd=python_app_dir)
    if result and result.returncode != 0:
        print("ERROR: Failed to install Python dependencies")
        print(result.stderr)
        return False
    
    # Run tests
    print("Running Python unit tests...")
    result = run_command("python -m pytest test_app.py -v", cwd=python_app_dir)
    
    if result is None:
        print("ERROR: Python tests timed out")
        return False
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    success = result.returncode == 0
    print(f"Python tests {'PASSED' if success else 'FAILED'}")
    return success

def run_go_tests(project_root):
    """Run Go unit tests"""
    print("\n" + "="*50)
    print("Running Go Tests")
    print("="*50)
    
    go_app_dir = project_root / "go-app"
    
    if not go_app_dir.exists():
        print("ERROR: go-app directory not found")
        return False
    
    # Download dependencies
    print("Downloading Go dependencies...")
    result = run_command("go mod download", cwd=go_app_dir)
    if result and result.returncode != 0:
        print("ERROR: Failed to download Go dependencies")
        print(result.stderr)
        return False
    
    # Run tests
    print("Running Go unit tests...")
    result = run_command("go test -v ./...", cwd=go_app_dir)
    
    if result is None:
        print("ERROR: Go tests timed out")
        return False
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    success = result.returncode == 0
    print(f"Go tests {'PASSED' if success else 'FAILED'}")
    return success

def run_rust_tests(project_root):
    """Run Rust unit tests"""
    print("\n" + "="*50)
    print("Running Rust Tests")
    print("="*50)
    
    rust_app_dir = project_root / "rust-app"
    
    if not rust_app_dir.exists():
        print("ERROR: rust-app directory not found")
        return False
    
    # Run tests
    print("Running Rust unit tests...")
    print("Running: cargo test -- --test-threads=1")
    
    result = subprocess.run(
        ["cargo", "test", "--", "--test-threads=1"],
        cwd=rust_app_dir,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    success = result.returncode == 0
    print(f"Rust tests {'PASSED' if success else 'FAILED'}")
    return success

def main():
    parser = argparse.ArgumentParser(description="Run unit tests for all microservices")
    parser.add_argument("--service", choices=["python", "go", "rust", "all"], 
                       default="all", help="Specify which service tests to run")
    parser.add_argument("--project-root", type=str, 
                       help="Path to project root directory")
    
    args = parser.parse_args()
    
    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        # Default to script's parent directory
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent
    
    print(f"Project root: {project_root}")
    
    if not project_root.exists():
        print(f"ERROR: Project root directory does not exist: {project_root}")
        sys.exit(1)
    
    results = {}
    
    if args.service in ["python", "all"]:
        results["python"] = run_python_tests(project_root)
    
    if args.service in ["go", "all"]:
        results["go"] = run_go_tests(project_root)
    
    if args.service in ["rust", "all"]:
        results["rust"] = run_rust_tests(project_root)
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for service, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{service.capitalize():<10} : {status}")
        if not passed:
            all_passed = False
    
    print("-" * 50)
    overall_status = "PASSED" if all_passed else "FAILED"
    print(f"{'Overall':<10} : {overall_status}")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
