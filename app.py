import streamlit as st
import pandas as pd

from utils.storage import (
    salvar_upload_relatorio,
    carregar_base_atual,
    obter_ultima_atualizacao,
    listar_historico_relatorio,
)
from utils.exports import dataframe_to_excel_bytes

st.set_page_config(
    page_title="Relatórios Empresariais",
    page_icon="📊",
    layout="wide"
)

st.set_option("client.showSidebarNavigation", False)


def aplicar_estilo_global():
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            section[data-testid="stSidebar"] {
                border-right: 1px solid #d9d9d9;
            }

            .relatorio-titulo {
                font-size: 2.6rem;
                font-weight: 800;
                letter-spacing: 0.5px;
                margin-bottom: 0.2rem;
            }

            .relatorio-subtitulo {
                color: #6b7280;
                font-size: 0.95rem;
                margin-bottom: 1.2rem;
            }

            .caixa-upload {
                padding: 1rem 1rem 0.5rem 1rem;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                background-color: #fafafa;
                margin-bottom: 1rem;
            }

            .secao-tabela {
                margin-top: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder(nome_relatorio: str):
    st.markdown(f'<div class="relatorio-titulo">{nome_relatorio}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="relatorio-subtitulo">Relatório ainda em construção.</div>',
        unsafe_allow_html=True
    )
    st.info("Essa área será desenvolvida nas próximas etapas.")


def render_controle_datas():
    nome_relatorio = "CONTROLE DE DATAS"
    pasta_relatorio = "controle_datas"

    st.markdown(f'<div class="relatorio-titulo">{nome_relatorio}</div>', unsafe_allow_html=True)

    ultima_atualizacao = obter_ultima_atualizacao(pasta_relatorio)
    if ultima_atualizacao:
        st.markdown(
            f'<div class="relatorio-subtitulo">Última atualização: {ultima_atualizacao}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="relatorio-subtitulo">Última atualização: aguardando upload</div>',
            unsafe_allow_html=True
        )

    with st.container():
        st.markdown('<div class="caixa-upload">', unsafe_allow_html=True)
        st.subheader("Upload da planilha")

        uploaded_file = st.file_uploader(
            "Selecione a planilha de CONTROLE DE DATAS",
            type=["xlsx", "xls"],
            key="upload_controle_datas",
            label_visibility="visible"
        )

        col_salvar, col_info = st.columns([1, 3])

        with col_salvar:
            salvar_click = st.button("Salvar planilha", type="primary", use_container_width=True)

        with col_info:
            st.caption("Ao salvar, o sistema guarda o histórico e atualiza a versão atual do relatório.")

        if salvar_click:
            if uploaded_file is None:
                st.warning("Selecione uma planilha antes de salvar.")
            else:
                caminho = salvar_upload_relatorio(uploaded_file, pasta_relatorio)
                st.success(f"Planilha salva com sucesso: {caminho}")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    df = carregar_base_atual(pasta_relatorio)

    if df is None or df.empty:
        st.info("Ainda não há base carregada para este relatório.")
        return

    st.markdown("---")
    st.subheader("Tabela")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=650
    )

    col_download, col_qtd, col_hist = st.columns([1.2, 1, 2])

    with col_download:
        arquivo_excel = dataframe_to_excel_bytes(df, "CONTROLE_DE_DATAS")
        st.download_button(
            label="📥 Baixar tabela",
            data=arquivo_excel,
            file_name="controle_de_datas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_qtd:
        st.metric("Registros", len(df))

    with col_hist:
        historico = listar_historico_relatorio(pasta_relatorio)
        if historico:
            st.caption("Histórico recente:")
            for item in historico[:5]:
                st.caption(f"• {item}")
        else:
            st.caption("Sem histórico de uploads.")


def main():
    aplicar_estilo_global()

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
                "TABELA GERAL POR CONSIGNATARIA",
            ]
        )

    if opcao == "CONTROLE DE DATAS":
        render_controle_datas()
    elif opcao == "ASSERTIVIDADE FRONT":
        render_placeholder("ASSERTIVIDADE FRONT")
    elif opcao == "INADIMPLENCIA GERAL":
        render_placeholder("INADIMPLENCIA GERAL")
    elif opcao == "INADIMPLENCIA 1º VENC":
        render_placeholder("INADIMPLENCIA 1º VENC")
    elif opcao == "INADIMPLENCIA ACIMA 5%":
        render_placeholder("INADIMPLENCIA ACIMA 5%")
    elif opcao == "TABELA GERAL POR CONSIGNATARIA":
        render_placeholder("TABELA GERAL POR CONSIGNATARIA")


if __name__ == "__main__":
    main()