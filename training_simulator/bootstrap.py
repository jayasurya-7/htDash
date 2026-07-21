"""
Bootstrap sys.path and import Config for training_simulator.

Mirrors the same pattern used by scripts/ CLI tools.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config

# Re-export for convenience
__all__ = ['PROJECT_ROOT', 'Config']
