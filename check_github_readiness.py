#!/usr/bin/env python3
"""
GitHub Upload Readiness Checker for SewageMapAI
=============================================

This script validates that the project is ready for GitHub upload by checking:
- File structure and required files
- Security considerations
- Documentation completeness
- Code quality issues
- Configuration validity

Run this before uploading to GitHub to ensure everything is properly configured.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import re

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class GitHubReadinessChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        
    def log_issue(self, message):
        """Log a critical issue"""
        self.issues.append(message)
        print(f"{Colors.RED}❌ {message}{Colors.END}")
        
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
        
    def log_success(self, message):
        """Log a success"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")

    def check_required_files(self):
        """Check if all required files exist"""
        print(f"\n{Colors.BOLD}📁 Checking Required Files...{Colors.END}")
        
        required_files = [
            'README.md',
            'LICENSE',
            'CONTRIBUTING.md',
            'SECURITY.md',
            '.gitignore',
            'run_app.py',
            'backend/app.py',
            'backend/requirements.txt',
            'frontend/package.json'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_success(f"{file_path} exists")
            else:
                self.log_issue(f"Missing required file: {file_path}")

    def check_gitignore(self):
        """Check .gitignore completeness"""
        print(f"\n{Colors.BOLD}🚫 Checking .gitignore...{Colors.END}")
        
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            self.log_issue(".gitignore file missing")
            return
            
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        required_patterns = [
            '__pycache__',
            'node_modules',
            '.env',
            'venv/',
            '*.log',
            'uploads/',
            '*.db'
        ]
        
        for pattern in required_patterns:
            if pattern in gitignore_content:
                self.log_success(f"Ignoring {pattern}")
            else:
                self.log_warning(f"Consider adding {pattern} to .gitignore")

    def check_sensitive_files(self):
        """Check for sensitive files that shouldn't be committed"""
        print(f"\n{Colors.BOLD}🔒 Checking for Sensitive Files...{Colors.END}")
        
        sensitive_patterns = [
            r'\.env$',
            r'\.key$',
            r'\.pem$',
            r'\.p12$',
            r'\.pfx$',
            r'config\.py$',
            r'secrets\.py$'
        ]
        
        sensitive_found = False
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip venv and node_modules
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '__pycache__', '.git']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)
                
                for pattern in sensitive_patterns:
                    if re.search(pattern, str(relative_path)):
                        self.log_issue(f"Sensitive file found: {relative_path}")
                        sensitive_found = True
                        break
        
        if not sensitive_found:
            self.log_success("No sensitive files found")

    def check_large_files(self):
        """Check for files that might be too large for GitHub"""
        print(f"\n{Colors.BOLD}📦 Checking File Sizes...{Colors.END}")
        
        large_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip venv and node_modules
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '__pycache__', '.git']]
            
            for file in files:
                file_path = Path(root) / file
                try:
                    size = file_path.stat().st_size
                    if size > 50 * 1024 * 1024:  # 50MB
                        relative_path = file_path.relative_to(self.project_root)
                        large_files.append((relative_path, size))
                except (OSError, PermissionError):
                    continue
        
        if large_files:
            for file_path, size in large_files:
                size_mb = size / (1024 * 1024)
                self.log_issue(f"Large file ({size_mb:.1f}MB): {file_path}")
        else:
            self.log_success("No large files found")

    def check_documentation(self):
        """Check documentation quality"""
        print(f"\n{Colors.BOLD}📖 Checking Documentation...{Colors.END}")
        
        readme_path = self.project_root / 'README.md'
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            required_sections = [
                'installation',
                'usage',
                'contributing',
                'license'
            ]
            
            for section in required_sections:
                if section.lower() in readme_content.lower():
                    self.log_success(f"README contains {section} section")
                else:
                    self.log_warning(f"README missing {section} section")
                    
            if len(readme_content) > 1000:
                self.log_success("README is comprehensive")
            else:
                self.log_warning("README might be too brief")
        else:
            self.log_issue("README.md missing")

    def check_package_files(self):
        """Check package configuration files"""
        print(f"\n{Colors.BOLD}📦 Checking Package Files...{Colors.END}")
        
        # Check requirements.txt
        req_path = self.project_root / 'backend' / 'requirements.txt'
        if req_path.exists():
            self.log_success("Backend requirements.txt exists")
            with open(req_path, 'r') as f:
                requirements = f.read()
            if 'flask' in requirements.lower():
                self.log_success("Flask dependency found")
            else:
                self.log_warning("Flask not found in requirements")
        else:
            self.log_issue("Backend requirements.txt missing")
        
        # Check package.json
        pkg_path = self.project_root / 'frontend' / 'package.json'
        if pkg_path.exists():
            self.log_success("Frontend package.json exists")
            try:
                with open(pkg_path, 'r') as f:
                    package_data = json.load(f)
                if 'react' in package_data.get('dependencies', {}):
                    self.log_success("React dependency found")
                if 'scripts' in package_data:
                    self.log_success("NPM scripts defined")
            except json.JSONDecodeError:
                self.log_issue("Invalid package.json format")
        else:
            self.log_issue("Frontend package.json missing")

    def check_security_config(self):
        """Check security configuration"""
        print(f"\n{Colors.BOLD}🛡️  Checking Security Configuration...{Colors.END}")
        
        # Check for hardcoded secrets in code
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        secrets_found = False
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '__pycache__', '.git']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for pattern in secret_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                relative_path = file_path.relative_to(self.project_root)
                                self.log_issue(f"Potential hardcoded secret in: {relative_path}")
                                secrets_found = True
                    except (OSError, PermissionError, UnicodeDecodeError):
                        continue
        
        if not secrets_found:
            self.log_success("No hardcoded secrets found")

    def check_git_status(self):
        """Check git repository status"""
        print(f"\n{Colors.BOLD}🌿 Checking Git Status...{Colors.END}")
        
        try:
            # Check if it's a git repository
            result = subprocess.run(['git', 'status'], 
                                  cwd=self.project_root, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                self.log_success("Git repository initialized")
                
                # Check for uncommitted changes
                if 'nothing to commit' in result.stdout:
                    self.log_success("No uncommitted changes")
                else:
                    self.log_warning("Uncommitted changes detected")
                    
            else:
                self.log_warning("Not a git repository - run 'git init' first")
                
        except FileNotFoundError:
            self.log_warning("Git not installed or not in PATH")

    def generate_report(self):
        """Generate final report"""
        print(f"\n{Colors.BOLD}📊 GitHub Upload Readiness Report{Colors.END}")
        print("=" * 50)
        
        if not self.issues and not self.warnings:
            print(f"{Colors.GREEN}🎉 Perfect! Your project is ready for GitHub upload!{Colors.END}")
            return True
        
        if self.issues:
            print(f"\n{Colors.RED}❌ Critical Issues ({len(self.issues)}):{Colors.END}")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  Warnings ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.issues:
            print(f"\n{Colors.RED}❌ Please fix critical issues before uploading to GitHub.{Colors.END}")
            return False
        else:
            print(f"\n{Colors.GREEN}✅ No critical issues! Safe to upload to GitHub.{Colors.END}")
            if self.warnings:
                print(f"{Colors.YELLOW}Consider addressing warnings for best practices.{Colors.END}")
            return True

    def run_all_checks(self):
        """Run all validation checks"""
        print(f"{Colors.BLUE}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════╗")
        print("║          🚀 GitHub Upload Readiness Check        ║")
        print("║                SewageMapAI Project               ║")
        print("╚═══════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        self.check_required_files()
        self.check_gitignore()
        self.check_sensitive_files()
        self.check_large_files()
        self.check_documentation()
        self.check_package_files()
        self.check_security_config()
        self.check_git_status()
        
        return self.generate_report()

def main():
    """Main function"""
    try:
        checker = GitHubReadinessChecker()
        success = checker.run_all_checks()
        
        if success:
            print(f"\n{Colors.GREEN}Ready to upload! Next steps:{Colors.END}")
            print("1. git add .")
            print("2. git commit -m 'Initial commit: SewageMapAI v2.0'")
            print("3. git remote add origin <your-github-repo-url>")
            print("4. git push -u origin main")
            
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}Please fix the issues above before uploading.{Colors.END}")
            sys.exit(1)
    except Exception as e:
        print(f"Error running checker: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
