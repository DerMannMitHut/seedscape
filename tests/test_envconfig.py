from __future__ import annotations

import importlib


def test_envconfig_uses_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("SEEDSCAPE_DATA_DIR", str(tmp_path))
    # Reload module to pick up env var at import time
    import seedscape.core.envconfig as envconfig

    envconfig = importlib.reload(envconfig)
    assert tmp_path == envconfig.SEEDSCAPE_DATA_DIR


def test_envconfig_frontend_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("SEEDSCAPE_FRONTEND_DIR", str(tmp_path))
    import seedscape.core.envconfig as envconfig

    envconfig = importlib.reload(envconfig)
    assert tmp_path == envconfig.SEEDSCAPE_FRONTEND_DIR
