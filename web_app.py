"""Interface web do assistente de texto."""
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app import build_messages

load_dotenv()
st.set_page_config(page_title="LLM Text Assistant", page_icon="🧠", layout="centered")
st.title("LLM Text Assistant")
st.caption("Resuma, explique ou revise textos com inteligência artificial.")
st.write("Projeto em Python para praticar integração com modelos de linguagem via API.")

choices = {"Resumir": "1", "Explicar": "2", "Revisar escrita": "3"}
with st.form("assistant_form"):
    action = st.selectbox("O que você quer fazer?", list(choices))
    text = st.text_area("Seu texto", height=200, max_chars=12000, placeholder="Cole um texto aqui...")
    submitted = st.form_submit_button("Gerar resposta", type="primary")

if "history" not in st.session_state:
    st.session_state.history = []

if submitted:
    if not text.strip():
        st.warning("Digite um texto para continuar.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("Configure OPENAI_API_KEY no arquivo .env para usar o assistente.")
    else:
        try:
            messages = build_messages(choices[action], text)
            with st.spinner("Processando texto..."):
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=30.0)
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=messages,
                    temperature=0.3,
                )
            result = response.choices[0].message.content or "O modelo não retornou conteúdo."
            st.session_state.history.insert(0, (action, result))
        except (OpenAIError, ValueError) as exc:
            st.error(f"Não foi possível gerar a resposta: {exc}")

if st.session_state.history:
    st.subheader("Resultados desta sessão")
    for index, (action, result) in enumerate(st.session_state.history):
        with st.expander(f"{action} · Resultado {len(st.session_state.history) - index}", expanded=index == 0):
            st.write(result)
    if st.button("Limpar histórico"):
        st.session_state.history = []
        st.rerun()

st.caption("O histórico fica apenas na sessão atual. A API pode gerar custos.")
