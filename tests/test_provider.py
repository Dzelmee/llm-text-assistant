import pytest
from unittest.mock import Mock
from provider import MAX_CHARS, generate_text


def test_rejects_long_text():
    with pytest.raises(ValueError, match="limite"):
        generate_text("1", "a" * (MAX_CHARS + 1), client=Mock())


def test_invalid_provider():
    with pytest.raises(ValueError, match="Provedor inválido"):
        generate_text("1", "Texto", provider="invalid", client=Mock())


def test_groq_response():
    client = Mock()
    client.chat.completions.create.return_value.choices = [Mock(message=Mock(content="Resumo gerado"))]
    assert generate_text("1", "Texto de exemplo", client=client) == "Resumo gerado"
    assert client.chat.completions.create.call_args.kwargs["messages"][1]["role"] == "user"


def test_empty_response():
    client = Mock()
    client.chat.completions.create.return_value.choices = [Mock(message=Mock(content=""))]
    with pytest.raises(ValueError, match="não retornou"):
        generate_text("1", "Texto", client=client)
