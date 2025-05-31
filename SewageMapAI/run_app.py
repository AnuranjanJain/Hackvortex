#!/usr/bin/env python3
"""
SewageMapAI - One-Click Application Launcher
============================================

This script automates the complete setup and launch of the SewageMapAI application.
It handles both backend (Flask) and frontend (React) servers automatically.

Usage: python run_app.py

Features:
- ✅ Checks prerequisites (Python, Node.js, npm)
- ✅ Creates Python virtual environment (if needed)
- ✅ Installs Python dependencies
- ✅ Installs Node.js dependencies (if needed)
- ✅ Starts Flask backend server (http://localhost:5000)
- ✅ Starts React frontend server (http://localhost:3000)
- ✅ Opens application in browser automatically
- ✅ Handles graceful shutdown with Ctrl+C

Author: SewageMapAI Team
Version: 2.0.0
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
import signal
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SewageMapAILauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.venv_dir = self.backend_dir / 'venv'
        
        self.backend_process = None
        self.frontend_process = None
        self.should_stop = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C and other termination signals"""
        print(f"\n{Colors.YELLOW}🛑 Shutting down SewageMapAI...{Colors.END}")
        self.should_stop = True
        self.cleanup()
        sys.exit(0)

    def print_header(self):
        """Print application header"""
        print(f"""
{Colors.BLUE}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                    🌊🤖 SewageMapAI Launcher                 ║
║               Next-Generation AI Infrastructure              ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}
""")

    def check_command(self, command, name):
        """Check if a command is available"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            print(f"{Colors.GREEN}✅ {name} is installed{Colors.END}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Colors.RED}❌ {name} is not installed{Colors.END}")
            return False

    def check_prerequisites(self):
        """Check if all required tools are installed"""
        print(f"{Colors.BOLD}🔍 Checking Prerequisites...{Colors.END}")
        
        python_ok = self.check_command('python', 'Python')
        node_ok = self.check_command('node', 'Node.js')
        npm_ok = self.check_command('npm', 'npm')
        
        if not all([python_ok, node_ok, npm_ok]):
            print(f"\n{Colors.RED}❌ Missing prerequisites. Please install:{Colors.END}")
            if not python_ok:
                print("   • Python 3.8+ from https://python.org")
            if not node_ok:
                print("   • Node.js 14+ from https://nodejs.org")
            if not npm_ok:
                print("   • npm (usually comes with Node.js)")
            sys.exit(1)
        
        print(f"{Colors.GREEN}✅ All prerequisites satisfied!{Colors.END}\n")

    def setup_backend(self):
        """Setup Python backend environment"""
        print(f"{Colors.BOLD}🐍 Setting up Python Backend...{Colors.END}")
        
        # Create virtual environment if it doesn't exist
        if not self.venv_dir.exists():
            print("   Creating Python virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)], 
                         check=True)
        
        # Determine the correct Python executable in venv
        if os.name == 'nt':  # Windows
            python_exe = self.venv_dir / 'Scripts' / 'python.exe'
            pip_exe = self.venv_dir / 'Scripts' / 'pip.exe'
        else:  # Unix-like
            python_exe = self.venv_dir / 'bin' / 'python'
            pip_exe = self.venv_dir / 'bin' / 'pip'
        
        # Install Python dependencies
        requirements_file = self.backend_dir / 'requirements.txt'
        if requirements_file.exists():
            print("   Installing Python dependencies...")
            subprocess.run([str(pip_exe), 'install', '-r', str(requirements_file)], 
                         check=True, cwd=self.backend_dir)
        
        print(f"{Colors.GREEN}✅ Backend setup complete!{Colors.END}\n")
        return python_exe

    def setup_frontend(self):
        """Setup Node.js frontend environment"""
        print(f"{Colors.BOLD}⚛️  Setting up React Frontend...{Colors.END}")
        
        package_json = self.frontend_dir / 'package.json'
        node_modules = self.frontend_dir / 'node_modules'
        
        if package_json.exists() and not node_modules.exists():
            print("   Installing Node.js dependencies...")
            subprocess.run(['npm', 'install'], cwd=self.frontend_dir, check=True)
        
        print(f"{Colors.GREEN}✅ Frontend setup complete!{Colors.END}\n")

    def start_backend(self, python_exe):
        """Start Flask backend server"""
        print(f"{Colors.BOLD}🚀 Starting Flask Backend Server...{Colors.END}")
        
        def run_backend():
            try:
                env = os.environ.copy()
                env['FLASK_ENV'] = 'development'
                
                self.backend_process = subprocess.Popen(
                    [str(python_exe), 'app.py'],
                    cwd=self.backend_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                
                # Monitor backend output
                for line in iter(self.backend_process.stdout.readline, ''):
                    if self.should_stop:
                        break
                    if 'Running on' in line:
                        print(f"{Colors.GREEN}✅ Backend server started: http://localhost:5000{Colors.END}")
                    
            except Exception as e:
                print(f"{Colors.RED}❌ Backend error: {e}{Colors.END}")
        
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait for backend to start
        time.sleep(3)

    def start_frontend(self):
        """Start React frontend server"""
        print(f"{Colors.BOLD}🌐 Starting React Frontend Server...{Colors.END}")
        
        def run_frontend():
            try:
                env = os.environ.copy()
                env['BROWSER'] = 'none'  # Prevent auto-opening browser
                
                self.frontend_process = subprocess.Popen(
                    ['npm', 'start'],
                    cwd=self.frontend_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                
                # Monitor frontend output
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if self.should_stop:
                        break
                    if 'webpack compiled' in line or 'Local:' in line:
                        print(f"{Colors.GREEN}✅ Frontend server started: http://localhost:3000{Colors.END}")
                        
            except Exception as e:
                print(f"{Colors.RED}❌ Frontend error: {e}{Colors.END}")
        
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()
        
        # Wait for frontend to start
        time.sleep(5)

    def open_browser(self):
        """Open the application in the default browser"""
        try:
            print(f"{Colors.BOLD}🌍 Opening application in browser...{Colors.END}")
            webbrowser.open('http://localhost:3000')
            print(f"{Colors.GREEN}✅ Application opened in browser!{Colors.END}\n")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not open browser automatically: {e}{Colors.END}")
            print(f"   Please manually visit: http://localhost:3000\n")

    def show_status(self):
        """Show application status and URLs"""
        print(f"{Colors.BOLD}📊 Application Status:{Colors.END}")
        print(f"   🌐 Frontend: {Colors.GREEN}http://localhost:3000{Colors.END}")
        print(f"   🐍 Backend:  {Colors.GREEN}http://localhost:5000{Colors.END}")
        print(f"   📖 API Docs: {Colors.BLUE}http://localhost:5000/api/docs{Colors.END}")
        print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all servers{Colors.END}")

    def cleanup(self):
        """Clean up processes on exit"""
        if self.backend_process and self.backend_process.poll() is None:
            print(f"{Colors.YELLOW}   Stopping backend server...{Colors.END}")
            self.backend_process.terminate()
            
        if self.frontend_process and self.frontend_process.poll() is None:
            print(f"{Colors.YELLOW}   Stopping frontend server...{Colors.END}")
            self.frontend_process.terminate()
        
        print(f"{Colors.GREEN}✅ Cleanup complete. Goodbye!{Colors.END}")

    def run(self):
        """Main application launcher"""
        try:
            self.print_header()
            self.check_prerequisites()
            
            # Setup environments
            python_exe = self.setup_backend()
            self.setup_frontend()
            
            # Start servers
            self.start_backend(python_exe)
            self.start_frontend()
            
            # Open browser and show status
            self.open_browser()
            self.show_status()
            
            # Keep the script running
            try:
                while not self.should_stop:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    """Entry point"""
    launcher = SewageMapAILauncher()
    launcher.run()

if __name__ == '__main__':
    main()
