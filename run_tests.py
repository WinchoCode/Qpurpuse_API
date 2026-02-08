import sys
import subprocess
import os

def run_tests():
    """Run pytest with coverage"""
    print("Running Qpurpose API Tests...")
    print("=" * 60)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONPATH'] = current_dir
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--cov=src',
        '--cov-report=term-missing',
        '--cov-report=html',
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return False

if __name__ == '__main__':
    success = run_tests()
    
    print("=" * 60)
    if success:
        print("All tests passed!")
        print("Coverage report generated in htmlcov/ folder")
        print("Open htmlcov/index.html in your browser")
    else:
        print("Some tests failed!")
    
    sys.exit(0 if success else 1)