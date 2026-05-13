"""pytest conftest — let tests run without `pip install -e .`.

Prepends src/ to sys.path so `import oltrack` works for in-tree dev.
For consumers who want to install: `pip install -e .[dev]`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
