"""
Test runner for Rumble Bot
"""
import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_tests():
    """Run all tests"""
    print("🧪 Running Rumble Bot Tests...")
    print("=" * 50)
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "--color=yes",
        str(Path(__file__).parent),
    ])
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
