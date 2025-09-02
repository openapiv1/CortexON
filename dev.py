#!/usr/bin/env python3
"""
CortexON Development Helper
Provides common development tasks without Docker
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        return False


def install_deps():
    """Install all dependencies"""
    print("📦 Installing Python dependencies...")
    
    root_dir = Path(__file__).parent
    cortex_dir = root_dir / "cortex_on"
    browser_dir = root_dir / "ta-browser" 
    frontend_dir = root_dir / "frontend"
    
    # Install Python dependencies
    if not run_command("pip install uv", cwd=root_dir):
        return False
        
    if not run_command("uv pip install -r requirements.txt --system", cwd=cortex_dir):
        return False
        
    if not run_command("uv pip install -r requirements.txt --system", cwd=browser_dir):
        return False
        
    # Install Playwright browsers
    if not run_command("playwright install chromium"):
        return False
        
    if not run_command("playwright install-deps"):
        return False
    
    # Install Node.js dependencies if Node is available
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        print("📦 Installing Node.js dependencies...")
        if not run_command("npm install", cwd=frontend_dir):
            return False
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  Node.js not found, skipping frontend dependencies")
    
    print("✅ All dependencies installed")
    return True


def clean():
    """Clean build artifacts and caches"""
    print("🧹 Cleaning build artifacts...")
    
    root_dir = Path(__file__).parent
    
    # Python cache cleanup
    run_command("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true", cwd=root_dir)
    run_command("find . -name '*.pyc' -delete", cwd=root_dir)
    
    # Node.js cleanup
    frontend_dir = root_dir / "frontend"
    if (frontend_dir / "node_modules").exists():
        run_command("rm -rf node_modules", cwd=frontend_dir)
    
    if (frontend_dir / "dist").exists():
        run_command("rm -rf dist", cwd=frontend_dir)
    
    print("✅ Cleanup complete")


def check_services():
    """Check if services are running"""
    print("🔍 Checking service status...")
    
    ports = {
        "CortexON Backend": 8081,
        "Agentic Browser": 8000,
        "Frontend": 3000
    }
    
    for service, port in ports.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service} is running on port {port}")
            else:
                print(f"❌ {service} is not running on port {port}")
        except Exception:
            print(f"❌ Could not check {service} on port {port}")


def lint():
    """Run linting on Python code"""
    print("🔍 Linting Python code...")
    
    root_dir = Path(__file__).parent
    
    # Check if linting tools are available
    try:
        subprocess.run(['flake8', '--version'], capture_output=True, check=True)
        print("Running flake8...")
        run_command("flake8 cortex_on ta-browser --max-line-length=100 --ignore=E203,W503", cwd=root_dir)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  flake8 not installed, skipping Python linting")
    
    try:
        subprocess.run(['black', '--version'], capture_output=True, check=True)
        print("Running black...")
        run_command("black --check cortex_on ta-browser", cwd=root_dir)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  black not installed, skipping Python formatting check")


def main():
    parser = argparse.ArgumentParser(description="CortexON Development Helper")
    parser.add_argument('command', choices=['install', 'clean', 'check', 'lint'], 
                       help='Command to run')
    
    if len(sys.argv) == 1:
        print("CortexON Development Helper")
        print("\nUsage: python dev.py <command>")
        print("\nAvailable commands:")
        print("  install  - Install all dependencies") 
        print("  clean    - Clean build artifacts and caches")
        print("  check    - Check service status")
        print("  lint     - Run code linting")
        print("\nTo start services:")
        print("  python start_all.py")
        return
    
    args = parser.parse_args()
    
    if args.command == 'install':
        install_deps()
    elif args.command == 'clean':
        clean()
    elif args.command == 'check':
        check_services()
    elif args.command == 'lint':
        lint()


if __name__ == "__main__":
    main()