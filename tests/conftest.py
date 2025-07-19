import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_openai_client():
    """Mock the OpenAI client."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(message=MagicMock(content="Test response from AI"))
        ]
    )
    return mock_client

@pytest.fixture(autouse=True)
def patch_openai(monkeypatch, mock_openai_client):
    """Patch the OpenAI client."""
    monkeypatch.setattr("base_orchestrator.OpenAI", lambda api_key: mock_openai_client)
