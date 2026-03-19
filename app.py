import streamlit as st
from pages.controle_datas import render_controle_datas

st.set_option("client.showSidebarNavigation", False)

st.set_page_config(
    page_title="Relatórios Empresariais",
    layout="wide"
)

st.sidebar.title("📊 Relatórios")

opcao = st.sidebar.radio(
    "Selecione um relatório:",
    [
        "CONTROLE DE DATAS",
        "ASSERTIVIDADE FRONT",
        "INADIMPLENCIA GERAL",
        "INADIMPLENCIA 1º VENC",
        "INADIMPLENCIA ACIMA 5%",
        "TABELA GERAL POR CONSIGNATARIA",
    ]
)

if opcao == "CONTROLE DE DATAS":
    render_controle_datas()
else:
    st.title(opcao)
    st.info("Relatório em construção.")