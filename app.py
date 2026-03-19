import streamlit as st
import pandas as pd
from pathlib import Path
from utils.storage import salvar_upload_relatorio, carregar_base_atual, obter_ultima_atualizacao
from utils.exports import dataframe_to_excel_bytes

st.set_page_config(
    page_title="Relatórios Empresariais",
    layout="wide"
)

# Segurança extra: esconde a navegação automática do Streamlit
st.set_option("client.showSidebarNavigation", False)


# =========================
# FUNÇÃO DA PÁGINA
# =========================
def render_controle_datas():
    st.title("CONTROLE DE DATAS")

    # Upload manual
    uploaded_file = st.file_uploader(
        "Selecione a planilha CONTROLE DE DATAS",
        type=["xlsx", "xls"],
        key="upload_controle_datas"
    )

    # Se enviou um novo arquivo, salva
    if uploaded_file is not None:
        caminho_salvo = salvar_upload_relatorio(uploaded_file, "controle_datas")
        st.success(f"Planilha salva com sucesso em: {caminho_salvo}")

    # Carrega sempre a última base salva
    df = carregar_base_atual("controle_datas")
    ultima_atualizacao = obter_ultima_atualizacao("controle_datas")

    if ultima_atualizacao:
        st.caption(f"Última atualização: {ultima_atualizacao}")
    else:
        st.caption("Última atualização: aguardando upload")

    if df is None or df.empty:
        st.info("Faça o upload da planilha para visualizar o relatório.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    arquivo_excel = dataframe_to_excel_bytes(df, "CONTROLE_DE_DATAS")

    st.download_button(
        label="📥 Baixar tabela",
        data=arquivo_excel,
        file_name="controle_de_datas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================
# SIDEBAR MANUAL
# =========================
with st.sidebar:
    st.markdown("## 📊 Relatórios")

    opcao = st.radio(
        "Selecione um relatório:",
        [
            "CONTROLE DE DATAS",
            "ASSERTIVIDADE FRONT",
            "INADIMPLENCIA GERAL",
            "INADIMPLENCIA 1º VENC",
            "INADIMPLENCIA ACIMA 5%",
            "TABELA GERAL POR CONSIGNATARIA"
        ]
    )

# =========================
# ROTEAMENTO
# =========================
if opcao == "CONTROLE DE DATAS":
    render_controle_datas()

elif opcao == "ASSERTIVIDADE FRONT":
    st.title("ASSERTIVIDADE FRONT")
    st.info("Relatório em construção.")

elif opcao == "INADIMPLENCIA GERAL":
    st.title("INADIMPLENCIA GERAL")
    st.info("Relatório em construção.")

elif opcao == "INADIMPLENCIA 1º VENC":
    st.title("INADIMPLENCIA 1º VENC")
    st.info("Relatório em construção.")

elif opcao == "INADIMPLENCIA ACIMA 5%":
    st.title("INADIMPLENCIA ACIMA 5%")
    st.info("Relatório em construção.")

elif opcao == "TABELA GERAL POR CONSIGNATARIA":
    st.title("TABELA GERAL POR CONSIGNATARIA")
    st.info("Relatório em construção.")