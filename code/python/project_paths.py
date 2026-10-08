"""Repository paths shared by relocated research calculation scripts."""

from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_ROOT.parent
PYTHON_ROOT = CODE_ROOT / "python"
DASHBOARD_ROOT = CODE_ROOT / "dashboard"
RESULTS_ROOT = PROJECT_ROOT / "results"
