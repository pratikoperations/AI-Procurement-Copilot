"""Static contract for the hosted Streamlit runtime dependency pair."""

from pathlib import Path


def test_streamlit_runtime_uses_validated_starlette_pair() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    assert "streamlit==1.59.1" in requirements
    assert "starlette==1.3.1" in requirements
