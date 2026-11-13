import pytest

from demo import EXAMPLES, demo_response


@pytest.mark.parametrize("task", ["1", "2", "3"])
def test_demo_examples_return_fixed_response(task):
    assert demo_response(task, EXAMPLES[task]["input"]) == EXAMPLES[task]["output"]


def test_demo_rejects_custom_text():
    with pytest.raises(ValueError, match="texto de exemplo"):
        demo_response("1", "Outro texto qualquer")


def test_demo_rejects_unknown_task():
    with pytest.raises(ValueError, match="Opção inválida"):
        demo_response("9", "Texto")
