import pytest

from app.config import settings
from scripts.reset_demo import reset_demo


def test_demo_reset_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", True)
    monkeypatch.setattr(settings, "allow_demo_reset", False)

    with pytest.raises(RuntimeError, match="ALLOW_DEMO_RESET=true"):
        reset_demo()