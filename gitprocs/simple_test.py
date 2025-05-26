# simple_test.py
import sys
print(f"Python path: {sys.path}")
print("Trying to find packages...")

import site
print(f"Site packages: {site.getsitepackages()}")

# Try to list installed packages
import subprocess
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
print("Installed packages:")
print(result.stdout)
