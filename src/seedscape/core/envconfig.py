import os
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[3]


def _get_dir(varname: str, default_subdir: str) -> Path:
    from_env = os.getenv(varname)
    if from_env:
        return Path(from_env).expanduser().resolve()
    else:
        return _repo_root / default_subdir


SEEDSCAPE_DATA_DIR = _get_dir("SEEDSCAPE_DATA_DIR", "data")

SEEDSCAPE_FRONTEND_DIR = _get_dir("SEEDSCAPE_FRONTEND_DIR", "frontend")
