"""
Debug script to identify and fix Python import issues
Run this first to diagnose your current setup
"""
import sys
import os
from pathlib import Path

def diagnose_import_issues():
    """Comprehensive diagnosis of import setup"""
    print("🔍 PYTHON IMPORT DIAGNOSIS")
    print("=" * 50)

    # Basic Python info
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).absolute()}")

    # Find project root (where this script is located)
    project_root = Path(__file__).parent.absolute()
    src_path = project_root / "src"

    print(f"\nProject root: {project_root}")
    print(f"Src path: {src_path}")
    print(f"Src exists: {src_path.exists()}")

    # Check Python path
    print(f"\n📁 PYTHON PATH ({len(sys.path)} entries):")
    for i, path in enumerate(sys.path):
        marker = "✓" if Path(path) == project_root else " "
        print(f"  {marker} {i}: {path}")

    if str(project_root) not in sys.path:
        print(f"❌ Project root NOT in Python path!")
        print(f"   Need to add: {project_root}")
    else:
        print(f"✓ Project root found in Python path")

    # Check project structure
    print(f"\n🏗️  PROJECT STRUCTURE:")
    if src_path.exists():
        for item in src_path.iterdir():
            if item.is_dir():
                init_file = item / "__init__.py"
                marker = "✓" if init_file.exists() else "❌"
                print(f"  {marker} 📁 {item.name}/ (__init__.py: {init_file.exists()})")

                # Check for Python files in each directory
                py_files = list(item.glob("*.py"))
                if py_files:
                    for py_file in py_files:
                        if py_file.name != "__init__.py":
                            print(f"      📄 {py_file.name}")
            else:
                print(f"    📄 {item.name}")
    else:
        print(f"❌ src/ directory not found!")

    # Check for critical __init__.py files
    print(f"\n📝 REQUIRED __init__.py FILES:")
    required_inits = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/slack/__init__.py",
        "src/services/__init__.py",
        "src/utils/__init__.py",
        "src/database/__init__.py"
    ]

    missing_inits = []
    for init_path in required_inits:
        full_path = project_root / init_path
        exists = full_path.exists()
        marker = "✓" if exists else "❌"
        print(f"  {marker} {init_path}")
        if not exists:
            missing_inits.append(full_path)

    # Check for pyproject.toml or setup.py
    print(f"\n📦 PACKAGING FILES:")
    pyproject = project_root / "pyproject.toml"
    setup_py = project_root / "setup.py"

    print(f"  {'✓' if pyproject.exists() else '❌'} pyproject.toml")
    print(f"  {'✓' if setup_py.exists() else '❌'} setup.py")

    # Attempt test imports
    print(f"\n🧪 TESTING IMPORTS:")

    # Add project root to path if missing
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"   Added {project_root} to sys.path")

    test_imports = [
        "src",
        "src.core",
        "src.core.config",
        "src.core.models",
        "src.utils",
        "src.utils.logging",
        "src.services"
    ]

    successful_imports = []
    failed_imports = []

    for import_name in test_imports:
        try:
            __import__(import_name)
            print(f"  ✓ {import_name}")
            successful_imports.append(import_name)
        except ImportError as e:
            print(f"  ❌ {import_name} - {e}")
            failed_imports.append((import_name, str(e)))
        except Exception as e:
            print(f"  ⚠️  {import_name} - {type(e).__name__}: {e}")
            failed_imports.append((import_name, f"{type(e).__name__}: {e}"))

    # Generate fix recommendations
    print(f"\n🔧 RECOMMENDED FIXES:")

    if missing_inits:
        print("1. CREATE MISSING __init__.py FILES:")
        for init_file in missing_inits:
            print(f"   touch {init_file}")
            # Actually create them
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.touch()
        print("   → Created missing __init__.py files!")

    if str(project_root) not in sys.path:
        print("2. ADD PROJECT ROOT TO PYTHONPATH:")
        print(f"   export PYTHONPATH=\"$PYTHONPATH:{project_root}\"")
        print(f"   # Or add this to your script:")
        print(f"   import sys; sys.path.insert(0, '{project_root}')")

    if not pyproject.exists() and not setup_py.exists():
        print("3. CREATE pyproject.toml FILE (see artifact)")
        print("4. INSTALL IN DEVELOPMENT MODE:")
        print("   pip install -e .")

    if failed_imports:
        print("5. FAILED IMPORTS TO FIX:")
        for import_name, error in failed_imports:
            print(f"   {import_name}: {error}")

    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  • Successful imports: {len(successful_imports)}")
    print(f"  • Failed imports: {len(failed_imports)}")
    print(f"  • Missing __init__.py files: {len(missing_inits)} (now created)")
    print(f"  • Project root in path: {'✓' if str(project_root) in sys.path else '❌'}")

    return {
        'project_root': project_root,
        'successful_imports': successful_imports,
        'failed_imports': failed_imports,
        'missing_inits_created': missing_inits
    }

def create_test_imports():
    """Create a comprehensive import test"""
    print(f"\n🧪 RUNNING COMPREHENSIVE IMPORT TESTS:")

    test_cases = [
        # Test basic package imports
        ("import src", "Basic src package"),
        ("from src import core", "Core subpackage"),
        ("from src.core import config", "Config module"),
        ("from src.core import models", "Models module"),
        ("from src.utils import logging", "Utils logging"),

        # Test specific class imports
        ("from src.core.models import TaskRequest", "TaskRequest class"),
        ("from src.utils.logging import StructuredLogger", "StructuredLogger class"),
    ]

    results = []
    for import_stmt, description in test_cases:
        try:
            exec(import_stmt)
            print(f"  ✓ {description}: {import_stmt}")
            results.append((import_stmt, True, None))
        except Exception as e:
            print(f"  ❌ {description}: {import_stmt} - {e}")
            results.append((import_stmt, False, str(e)))

    return results

if __name__ == "__main__":
    diagnosis = diagnose_import_issues()
    test_results = create_test_imports()

    print(f"\n✅ Diagnosis complete!")
    print(f"Run this script again to see if issues are resolved.")
