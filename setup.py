#!/usr/bin/env python3
"""
CortexON Setup Script
Replaces Docker setup with pure Python installation and service management
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class CortexONSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.cortex_on_dir = self.root_dir / "cortex_on"
        self.ta_browser_dir = self.root_dir / "ta-browser"
        self.frontend_dir = self.root_dir / "frontend"
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        if sys.version_info < (3, 10):
            print("❌ Python 3.10 or higher is required")
            sys.exit(1)
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    
    def check_node_version(self):
        """Check if Node.js is available for frontend"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Node.js {version} found")
                return True
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js 18+ for frontend development")
            return False
        return False
    
    def install_uv(self):
        """Install uv package manager if not available"""
        try:
            subprocess.run(['uv', '--version'], capture_output=True, check=True)
            print("✅ uv package manager is already installed")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("📦 Installing uv package manager...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], check=True)
            print("✅ uv package manager installed")
    
    def setup_cortex_on(self):
        """Setup cortex_on backend service"""
        print("\n🔧 Setting up CortexON backend...")
        os.chdir(self.cortex_on_dir)
        
        # Install dependencies
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt', '--system'], check=True)
        print("✅ CortexON backend dependencies installed")
        
        # Return to root directory
        os.chdir(self.root_dir)
    
    def setup_ta_browser(self):
        """Setup ta-browser service"""
        print("\n🔧 Setting up Agentic Browser...")
        os.chdir(self.ta_browser_dir)
        
        # Install dependencies
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt', '--system'], check=True)
        
        # Install Playwright browsers
        print("📦 Installing Playwright browsers...")
        subprocess.run(['playwright', 'install', 'chromium'], check=True)
        subprocess.run(['playwright', 'install-deps'], check=True)
        print("✅ Agentic Browser dependencies and browsers installed")
        
        # Return to root directory
        os.chdir(self.root_dir)
    
    def setup_frontend(self):
        """Setup frontend service"""
        if not self.check_node_version():
            print("⚠️  Skipping frontend setup due to missing Node.js")
            return False
            
        print("\n🔧 Setting up Frontend...")
        os.chdir(self.frontend_dir)
        
        # Install dependencies
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Frontend dependencies installed")
        
        # Return to root directory
        os.chdir(self.root_dir)
        return True
    
    def create_startup_scripts(self):
        """Create scripts to start services"""
        print("\n📝 Creating startup scripts...")
        
        # Create start_cortex_on.py
        start_cortex_script = self.root_dir / "start_cortex_on.py"
        with open(start_cortex_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Change to cortex_on directory
cortex_dir = Path(__file__).parent / "cortex_on"
os.chdir(cortex_dir)

# Set Python path to ensure local imports work
sys.path.insert(0, str(cortex_dir))
os.environ['PYTHONPATH'] = str(cortex_dir)

print(f"🚀 Starting CortexON Backend from {cortex_dir}")
print("📍 API will be available at http://localhost:8081")

# Start the service
import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
''')
        
        # Create start_ta_browser.py
        start_browser_script = self.root_dir / "start_ta_browser.py"
        with open(start_browser_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Change to ta-browser directory  
browser_dir = Path(__file__).parent / "ta-browser"
os.chdir(browser_dir)

# Set Python path to ensure local imports work
sys.path.insert(0, str(browser_dir))
os.environ['PYTHONPATH'] = str(browser_dir)

print(f"🚀 Starting Agentic Browser from {browser_dir}")
print("📍 API will be available at http://localhost:8000")

# Start the service
import uvicorn
if __name__ == "__main__":
    uvicorn.run("core.server.main:app", host="0.0.0.0", port=8000, workers=1)
''')
        
        # Create start_frontend.py
        start_frontend_script = self.root_dir / "start_frontend.py"
        with open(start_frontend_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

# Change to frontend directory
frontend_dir = Path(__file__).parent / "frontend"

# Check if Node.js is available
try:
    subprocess.run(['node', '--version'], capture_output=True, check=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    print("❌ Node.js not found. Please install Node.js 18+ to run the frontend.")
    sys.exit(1)

# Check if node_modules exists
if not (frontend_dir / "node_modules").exists():
    print("📦 Installing frontend dependencies...")
    os.chdir(frontend_dir)
    subprocess.run(["npm", "install"], check=True)
    print("✅ Frontend dependencies installed")

os.chdir(frontend_dir)
print(f"🚀 Starting Frontend from {frontend_dir}")
print("📍 Frontend will be available at http://localhost:3000")

# Start the frontend development server
if __name__ == "__main__":
    subprocess.run(["npm", "run", "dev"], check=True)
''')
        
        # Create start_all.py
        start_all_script = self.root_dir / "start_all.py"
        with open(start_all_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
import subprocess
import threading
import time
import sys
from pathlib import Path

def start_service(script_name, service_name):
    """Start a service script"""
    try:
        print(f"🚀 Starting {service_name}...")
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start {service_name}: {e}")
    except KeyboardInterrupt:
        print(f"🛑 Stopping {service_name}...")

if __name__ == "__main__":
    root_dir = Path(__file__).parent
    
    # Start services in separate threads
    services = [
        ("start_cortex_on.py", "CortexON Backend"),
        ("start_ta_browser.py", "Agentic Browser"),  
        ("start_frontend.py", "Frontend")
    ]
    
    threads = []
    
    try:
        for script, name in services:
            script_path = root_dir / script
            if script_path.exists():
                thread = threading.Thread(target=start_service, args=(str(script_path), name))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                time.sleep(3)  # Stagger startup more
            else:
                print(f"⚠️  {script} not found, skipping {name}")
        
        print("\\n" + "=" * 60)
        print("✅ All services started!")
        print("📍 Access points:")
        print("   - CortexON Backend: http://localhost:8081 (API Docs: /docs)")
        print("   - Agentic Browser: http://localhost:8000 (API Docs: /docs)") 
        print("   - Frontend: http://localhost:3000")
        print("=" * 60)
        print("🔄 Services are running. Press Ctrl+C to stop all services.\\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n🛑 Stopping all services...")
        sys.exit(0)
''')
        
        # Make scripts executable
        for script in [start_cortex_script, start_browser_script, start_frontend_script, start_all_script]:
            script.chmod(0o755)
        
        print("✅ Startup scripts created:")
        print(f"   - {start_cortex_script.name} - Start CortexON backend only")
        print(f"   - {start_browser_script.name} - Start Agentic Browser only") 
        print(f"   - {start_frontend_script.name} - Start Frontend only")
        print(f"   - {start_all_script.name} - Start all services")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 CortexON Python Setup Starting...")
        print("=" * 50)
        
        self.check_python_version()
        self.install_uv()
        
        try:
            self.setup_cortex_on()
            self.setup_ta_browser()
            frontend_ok = self.setup_frontend()
            self.create_startup_scripts()
            
            print("\n" + "=" * 50)
            print("🎉 CortexON Python Setup Complete!")
            print("\n📋 Next steps:")
            print("1. Create a .env file with your API keys (see README.md)")
            print("2. Run: python start_all.py")
            print("3. Access the services at:")
            print("   - Frontend: http://localhost:3000")
            print("   - CortexON Backend: http://localhost:8081")
            print("   - Agentic Browser: http://localhost:8000")
            
            if not frontend_ok:
                print("\n⚠️  Frontend setup was skipped due to missing Node.js")
                print("   Install Node.js 18+ to enable frontend development")
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    setup = CortexONSetup()
    setup.run_setup()