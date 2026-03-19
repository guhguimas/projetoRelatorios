import streamlit as st
import pandas as pd
from datetime import datetime
from utils.exports import dataframe_to_excel_bytes

def render_controle_datas():
    st.title("CONTROLE DE DATAS")

    uploaded_file = st.file_uploader(
        "Selecione a planilha CONTROLE DE DATAS",
        type=["xlsx", "xls"],
        key="upload_controle_datas"
    )

    if uploaded_file is None:
        st.caption("Última atualização: aguardando upload")
        st.info("Faça o upload da planilha para visualizar o relatório.")
        return

    df = pd.read_excel(uploaded_file)

    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.caption(f"Última atualização: {ultima_atualizacao}")

    st.dataframe(df, use_container_width=True, hide_index=True)

    arquivo_excel = dataframe_to_excel_bytes(df, "CONTROLE_DE_DATAS")

    st.download_button(
        label="📥 Baixar tabela",
        data=arquivo_excel,
        file_name="controle_de_datas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )