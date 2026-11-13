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

@pytest.mark.parametrize("size,expected", [
    ("Curto", "até 70 palavras"),
    ("Médio", "100 a 150 palavras"),
    ("Detalhado", "200 a 300 palavras"),
])
def test_summary_length_instruction(size, expected):
    messages = build_messages("1", "Texto de teste", summary_length=size)
    assert expected in messages[1]["content"]


def test_invalid_summary_length():
    with pytest.raises(ValueError, match="Tamanho de resumo"):
        build_messages("1", "Texto", summary_length="Gigante")


def test_other_actions_do_not_change_with_summary_length():
    assert build_messages("2", "Texto", summary_length="Curto") == build_messages("2", "Texto")

def test_summary_requests_readable_numbers_without_changing_values():
    message = build_messages("1", "850000 habitantes e R$ 4800000000")[1]["content"]
    assert "850 mil habitantes" in message
    assert "R$ 4,8 bilhões" in message
    assert "Não arredonde números" in message


def test_other_actions_do_not_receive_summary_number_guidance():
    message = build_messages("2", "Texto")[1]["content"]
    assert "850 mil habitantes" not in message
