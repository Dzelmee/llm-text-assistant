"""Exemplos fixos para demonstrar a interface sem consumir a API."""

EXAMPLES = {
    "1": {
        "input": "A inteligência artificial generativa permite criar textos, analisar informações e automatizar tarefas. Por meio de APIs, desenvolvedores conseguem integrar modelos de linguagem a aplicações e melhorar a produtividade.",
        "output": "A inteligência artificial generativa ajuda a criar e analisar textos e automatizar tarefas. Sua integração por APIs permite desenvolver ferramentas que aumentam a produtividade.",
    },
    "2": {
        "input": "Uma API REST permite a comunicação entre sistemas por meio de requisições HTTP e utiliza recursos identificados por URLs.",
        "output": "Uma API REST funciona como uma ponte entre programas. Um aplicativo envia uma solicitação pela internet e outro sistema responde com os dados ou a ação solicitada. As URLs indicam o recurso que está sendo acessado.",
    },
    "3": {
        "input": "Eu fiz um projeto que ele ajuda as pessoas a escrever melhor e também faz resumo de textos.",
        "output": "Desenvolvi um projeto que ajuda as pessoas a escrever melhor e também permite resumir textos.",
    },
}


def demo_response(task: str, text: str) -> str:
    """Retorna uma saída fixa somente quando o texto corresponde ao exemplo."""
    if task not in EXAMPLES:
        raise ValueError("Opção inválida.")
    if text.strip() != EXAMPLES[task]["input"]:
        raise ValueError("No modo demonstração, use o texto de exemplo fornecido.")
    return EXAMPLES[task]["output"]
