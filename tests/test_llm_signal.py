"""Tests for LLM signal — uses injectable client to avoid Groq API calls."""
import pytest
from unittest.mock import MagicMock
from app.signals.llm_signal import classify_with_llm


def _mock_client(ai_probability):
    """Build a mock Groq client returning the given ai_probability."""
    client = MagicMock()
    msg = MagicMock()
    msg.content = f'{{"ai_probability": {ai_probability}}}'
    client.chat.completions.create.return_value.choices = [MagicMock(message=msg)]
    return client


def test_returns_parsed_score():
    result = classify_with_llm("some text", client=_mock_client(0.82))
    assert result == pytest.approx(0.82)


def test_clamps_above_1():
    result = classify_with_llm("some text", client=_mock_client(1.5))
    assert result == 1.0


def test_clamps_below_0():
    result = classify_with_llm("some text", client=_mock_client(-0.3))
    assert result == 0.0


def test_boundary_exactly_1():
    result = classify_with_llm("some text", client=_mock_client(1.0))
    assert result == 1.0


def test_boundary_exactly_0():
    result = classify_with_llm("some text", client=_mock_client(0.0))
    assert result == 0.0


def test_unparseable_json_raises():
    client = MagicMock()
    msg = MagicMock()
    msg.content = "not json at all"
    client.chat.completions.create.return_value.choices = [MagicMock(message=msg)]
    with pytest.raises(ValueError, match="unparseable"):
        classify_with_llm("some text", client=client)


def test_missing_key_raises():
    client = MagicMock()
    msg = MagicMock()
    msg.content = '{"wrong_key": 0.5}'
    client.chat.completions.create.return_value.choices = [MagicMock(message=msg)]
    with pytest.raises(ValueError):
        classify_with_llm("some text", client=client)


def test_prompt_includes_text():
    client = _mock_client(0.5)
    classify_with_llm("unique_marker_xyz", client=client)
    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    assert any("unique_marker_xyz" in m["content"] for m in messages)
