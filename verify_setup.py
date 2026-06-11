#!/usr/bin/env python
"""
Setup Verification Script - Verifies all prerequisites are met
"""

import subprocess
import sys
import os
from pathlib import Path


class SetupVerifier:
    """Verify setup prerequisites"""

    def __init__(self):
        self.results = []
        self.warnings = []

    def check_command(self, cmd, name):
        """Check if a command exists"""
        try:
            subprocess.run(
                cmd, 
                capture_output=True, 
                shell=True,
                check=True,
                timeout=5
            )
            self.results.append((name, "✓", "Found"))
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            self.results.append((name, "✗", "Not found or not running"))
            return False

    def check_directory(self, path, name):
        """Check if directory exists"""
        exists = Path(path).exists()
        status = "✓" if exists else "✗"
        self.results.append((name, status, str(path)))
        return exists

    def check_file(self, path, name):
        """Check if file exists"""
        exists = Path(path).exists()
        status = "✓" if exists else "✗"
        self.results.append((name, status, str(path)))
        return exists

    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")

    def print_results(self):
        """Print all results"""
        for item, status, detail in self.results:
            print(f"{status} {item:<40} {detail}")

    def run_verification(self):
        """Run all verifications"""
        self.print_header("MARKETPLACE SETUP VERIFICATION")

        # System dependencies
        self.print_header("1. System Dependencies")
        python_ok = self.check_command("python --version", "Python 3.9+")
        node_ok = self.check_command("node --version", "Node.js 18+")
        npm_ok = self.check_command("npm --version", "npm")

        # Database & Cache
        self.print_header("2. Services (Optional - Can use Docker)")
        postgres_ok = self.check_command(
            "psql --version",
            "PostgreSQL"
        )
        redis_ok = self.check_command(
            "redis-cli --version",
            "Redis"
        )

        if not postgres_ok:
            self.warnings.append(
                "PostgreSQL not found. Use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15"
            )
        if not redis_ok:
            self.warnings.append(
                "Redis not found. Use Docker: docker run -d -p 6379:6379 redis:7"
            )

        # Project directories
        self.print_header("3. Project Structure")
        base = "."
        backend_ok = self.check_directory(
            f"{base}/marketplace-backend",
            "Backend Directory"
        )
        seller_ok = self.check_directory(
            f"{base}/seller-portal",
            "Seller Portal Directory"
        )
        storefront_ok = self.check_directory(
            f"{base}/customer-storefront",
            "Storefront Directory"
        )

        # Backend files
        self.print_header("4. Backend Files")
        main_ok = self.check_file(
            f"{base}/marketplace-backend/main.py",
            "Backend main.py"
        )
        config_ok = self.check_file(
            f"{base}/marketplace-backend/config.py",
            "Backend config.py"
        )
        requirements_ok = self.check_file(
            f"{base}/marketplace-backend/requirements.txt",
            "Backend requirements.txt"
        )

        # Frontend files
        self.print_header("5. Frontend Files")
        seller_pkg = self.check_file(
            f"{base}/seller-portal/package.json",
            "Seller Portal package.json"
        )
        storefront_pkg = self.check_file(
            f"{base}/customer-storefront/package.json",
            "Storefront package.json"
        )

        # Documentation
        self.print_header("6. Documentation")
        quickstart_ok = self.check_file(
            f"{base}/QUICKSTART.md",
            "QUICKSTART.md"
        )
        arch_ok = self.check_file(
            f"{base}/ARCHITECTURE.md",
            "ARCHITECTURE.md"
        )
        deploy_ok = self.check_file(
            f"{base}/DEPLOYMENT_GUIDE.md",
            "DEPLOYMENT_GUIDE.md"
        )

        # Print results
        self.print_header("VERIFICATION RESULTS")
        self.print_results()

        # Warnings
        if self.warnings:
            self.print_header("WARNINGS")
            for warning in self.warnings:
                print(f"⚠ {warning}\n")

        # Summary
        self.print_header("NEXT STEPS")

        if python_ok and node_ok and backend_ok and seller_ok and storefront_ok:
            print("✓ All essential components found!\n")
            print("Next steps:")
            print("  1. Start PostgreSQL & Redis (if not running)")
            print("  2. cd marketplace-backend")
            print("  3. python -m venv venv")
            print("  4. source venv/bin/activate  # Windows: venv\\Scripts\\activate")
            print("  5. pip install -r requirements.txt")
            print("  6. python init_db.py")
            print("  7. python -m uvicorn main:app --reload")
            print("\nThen in separate terminals:")
            print("  cd seller-portal && npm install && npm run dev")
            print("  cd customer-storefront && npm install && npm run dev")
            print("\nRead QUICKSTART.md for detailed instructions.")
        else:
            print("✗ Some required components are missing.\n")
            print("Required:")
            print("  - Python 3.9+ installed globally")
            print("  - Node.js 18+ installed globally")
            print("  - All three project directories")
            print("  - Backend files (main.py, config.py, requirements.txt)")
            print("  - Frontend package.json files\n")

        return python_ok and node_ok and backend_ok and seller_ok and storefront_ok


def main():
    """Run verification"""
    verifier = SetupVerifier()
    success = verifier.run_verification()

    print("\n" + "="*60)
    if success:
        print("  ✓ SETUP VERIFIED - Ready to proceed!")
    else:
        print("  ✗ SETUP INCOMPLETE - Fix issues above")
    print("="*60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
