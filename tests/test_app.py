import pytest
from app import build_messages


def test_build_messages_includes_text_and_instruction():
    messages = build_messages("1", "  Exemplo de texto  ")
    assert messages[0]["role"] == "system"
    assert "Resuma" in messages[1]["content"]
    assert "Exemplo de texto" in messages[1]["content"]


@pytest.mark.parametrize("task,text", [("9", "texto"), ("1", "  ")])
def test_invalid_input(task, text):
    with pytest.raises(ValueError):
        build_messages(task, text)
