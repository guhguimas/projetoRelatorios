import streamlit as st
import pandas as pd

def is_admin():
    try:
        token = st.query_params.get("admin")
        return token == st.secrets.get("ADMIN_TOKEN")
    except Exception:
        return False

admin = is_admin()

# ==============================
# 📦 IMPORTS INTERNOS
# ==============================
from utils.storage import (
    salvar_upload_relatorio,
    carregar_base_atual,
    obter_ultima_atualizacao,
    listar_historico_relatorio,
)
from utils.exports import dataframe_to_excel_bytes

# ==============================
# ⚙ CONFIG PAGE
# ==============================
st.set_page_config(
    page_title="Relatórios Empresariais",
    page_icon="📊",
    layout="wide"
)

st.set_option("client.showSidebarNavigation", False)

# ==============================
# 🎨 ESTILO GLOBAL
# ==============================
def aplicar_estilo_global():
    st.markdown(
        """
        <style>
            .relatorio-titulo {
                font-size: 2.6rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
            }

            .relatorio-subtitulo {
                color: #6b7280;
                font-size: 0.95rem;
                margin-bottom: 1.2rem;
            }

            .caixa-upload {
                padding: 1rem;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background-color: #fafafa;
                margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================
# 🧠 FUNÇÃO CORREÇÃO HEADER
# ==============================
def ajustar_header(df):
    """
    Corrige o cabeçalho automaticamente:
    - encontra linha com CONVENIO
    - remove linhas acima
    - remove colunas vazias
    - renomeia colunas duplicadas
    """

    # Encontrar linha do header
    for i, row in df.iterrows():
        if "CONVENIO" in str(row.values):
            df.columns = df.iloc[i]
            df = df.iloc[i+1:]
            df = df.reset_index(drop=True)
            break

    # Remover colunas totalmente vazias
    df = df.loc[:, df.columns.notna()]

    # Converter nomes para string
    df.columns = [str(col).strip() for col in df.columns]

    # 🔥 Resolver duplicados (SLA vira SLA_1, SLA_2...)
    cols = []
    count = {}

    for col in df.columns:
        if col in count:
            count[col] += 1
            cols.append(f"{col}_{count[col]}")
        else:
            count[col] = 0
            cols.append(col)

    df.columns = cols

    return df

# ==============================
# 📄 PLACEHOLDER
# ==============================
def render_placeholder(nome):
    st.markdown(f'<div class="relatorio-titulo">{nome}</div>', unsafe_allow_html=True)
    st.info("Relatório em construção.")

# ==============================
# 📊 CONTROLE DE DATAS
# ==============================
def render_controle_datas():
    nome_relatorio = "CONTROLE DE DATAS"
    pasta_relatorio = "controle_datas"

    st.markdown(f'<div class="relatorio-titulo">{nome_relatorio}</div>', unsafe_allow_html=True)

    # Última atualização
    ultima = obter_ultima_atualizacao(pasta_relatorio)
    if ultima:
        st.markdown(f'<div class="relatorio-subtitulo">Última atualização: {ultima}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="relatorio-subtitulo">Aguardando upload</div>', unsafe_allow_html=True)

    # ==============================
    # 🔒 UPLOAD (SÓ ADMIN)
    # ==============================
    with st.container():
        st.markdown('<div class="caixa-upload">', unsafe_allow_html=True)
        st.subheader("Upload da planilha")

        if admin:
            st.success("Modo administrador ativo")

            uploaded_file = st.file_uploader(
                "Selecione a planilha",
                type=["xlsx", "xls"]
            )

            if st.button("Salvar planilha"):
                if uploaded_file:
                    salvar_upload_relatorio(uploaded_file, pasta_relatorio)
                    st.success("Upload realizado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Selecione um arquivo")
        else:
            # 👇 NÃO MOSTRA upload
            st.info("Visualização disponível")

        st.markdown("</div>", unsafe_allow_html=True)

    # ==============================
    # 📥 CARREGAR BASE
    # ==============================
    df = carregar_base_atual(pasta_relatorio)

    if df is None or df.empty:
        st.info("Nenhuma base carregada ainda.")
        return

    # ==============================
    # 🧠 AJUSTAR HEADER
    # ==============================
    df = ajustar_header(df)

    # ==============================
    # 📊 TABELA
    # ==============================
    st.markdown("---")
    # st.subheader("Tabela")

    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        height=650
    )

    # ==============================
    # 📥 DOWNLOAD + INFO
    # ==============================
    col1, col2, col3 = st.columns(3)

    with col1:
        excel = dataframe_to_excel_bytes(df, "controle")
        st.download_button("📥 Baixar Excel", data=excel, file_name="controle.xlsx")

    with col2:
        st.metric("Registros", len(df))

    with col3:
        hist = listar_historico_relatorio(pasta_relatorio)
        if hist:
            st.caption("Histórico:")
            for h in hist[:5]:
                st.caption(f"• {h}")

# ==============================
# 🚀 MAIN
# ==============================
def main():
    aplicar_estilo_global()

    with st.sidebar:
        opcao = st.radio(
            "Relatórios",
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