import streamlit as st
import pandas as pd

# ==============================
# 🔒 ADMIN VIA TOKEN
# ==============================
def is_admin():
    try:
        token = st.query_params.get("admin")
        return token == st.secrets.get("ADMIN_TOKEN")
    except:
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
    st.markdown("""
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
    """, unsafe_allow_html=True)

# ==============================
# 🧠 AJUSTE HEADER
# ==============================
def ajustar_header(df):
    for i, row in df.iterrows():
        if "CONVENIO" in str(row.values):
            df.columns = df.iloc[i]
            df = df.iloc[i+1:]
            df = df.reset_index(drop=True)
            break

    df = df.loc[:, df.columns.notna()]
    df.columns = [str(col).strip() for col in df.columns]

    # remover duplicados
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
# 🧠 LIMPAR SLA
# ==============================
def limpar_sla(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor)
    valor = valor.replace("dia(s)", "d")
    valor = valor.replace("hora(s)", "h")
    valor = valor.replace("minutos", "m")
    valor = valor.replace("e", "")
    return valor.strip()


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
    # 🔒 UPLOAD
    # ==============================
    with st.container():
        st.markdown('<div class="caixa-upload">', unsafe_allow_html=True)
        st.subheader("Upload da planilha")

        if admin:
            st.success("Modo administrador ativo")

            uploaded_file = st.file_uploader("Selecione a planilha", type=["xlsx", "xls"])

            if st.button("Salvar planilha"):
                if uploaded_file:
                    salvar_upload_relatorio(uploaded_file, pasta_relatorio)
                    st.success("Upload realizado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Selecione um arquivo")
        else:
            st.info("Visualização disponível")

        st.markdown("</div>", unsafe_allow_html=True)

    # ==============================
    # 📥 CARREGAR BASE
    # ==============================
    df = carregar_base_atual(pasta_relatorio)

    if df is None or df.empty:
        st.info("Nenhuma base carregada ainda.")
        return

    df = ajustar_header(df)

    # ==============================
    # 🎛 FILTROS
    # ==============================
    st.markdown("### 🔎 Filtros")

    col1, col2 = st.columns(2)

    with col1:
        if "CONVENIO" in df.columns:
            convenios = sorted(df["CONVENIO"].dropna().unique())
            filtro_convenio = st.multiselect("Convênio", convenios)
        else:
            filtro_convenio = []

    with col2:
        col_data = None
        for col in df.columns:
            if "DATA" in col.upper() or "CHEGADA" in col.upper():
                col_data = col
                break

        if col_data:
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
            data_min = df[col_data].min()
            data_max = df[col_data].max()

            filtro_data = st.date_input("Período", value=(data_min, data_max))
        else:
            filtro_data = None

    # ==============================
    # 🧠 APLICAR FILTROS
    # ==============================
    df_filtrado = df.copy()

    if filtro_convenio:
        df_filtrado = df_filtrado[df_filtrado["CONVENIO"].isin(filtro_convenio)]

    if filtro_data and col_data:
        inicio, fim = filtro_data
        df_filtrado = df_filtrado[
            (df_filtrado[col_data] >= pd.to_datetime(inicio)) &
            (df_filtrado[col_data] <= pd.to_datetime(fim))
        ]

    # ==============================
    # 🧠 LIMPAR SLA
    # ==============================
    for col in df_filtrado.columns:
        if "SLA" in col.upper():
            df_filtrado[col] = df_filtrado[col].apply(limpar_sla)

    # ==============================
    # 📊 TABELA
    # ==============================
    st.data_editor(
        df_filtrado,
        width="stretch",
        hide_index=True,
        height=650,
        num_rows="fixed",
        column_config={
            "CONVENIO": st.column_config.TextColumn("Convênio"),
        }
    )

    # ==============================
    # 📥 DOWNLOAD + HISTÓRICO
    # ==============================
    col1, col2, col3 = st.columns(3)

    with col1:
        excel = dataframe_to_excel_bytes(df_filtrado, "controle")
        st.download_button("📥 Baixar Excel", data=excel, file_name="controle.xlsx")

    with col2:
        st.metric("Registros exibidos", len(df_filtrado))

    with col3:
        hist = listar_historico_relatorio(pasta_relatorio)
        if hist:
            st.caption("Histórico:")
            for h in hist[:5]:
                st.caption(f"• {h}")

# ==============================
# 📄 PLACEHOLDER
# ==============================
def render_placeholder(nome):
    st.markdown(f'<div class="relatorio-titulo">{nome}</div>', unsafe_allow_html=True)
    st.info("Relatório em construção.")

def aplicar_filtros(df):

    st.markdown("### 🔎 Filtros")

    col1, col2 = st.columns(2)

    # ===== CONVÊNIO =====
    with col1:
        if "CONVENIO" in df.columns:
            lista = sorted(df["CONVENIO"].dropna().unique())

            filtro_convenio = st.multiselect(
                "Convênio",
                options=lista
            )
        else:
            filtro_convenio = []

    # ===== DATA =====
    with col2:
        col_data = None

        for col in df.columns:
            if "DATA" in col.upper() or "CHEGADA" in col.upper():
                col_data = col
                break

        if col_data:
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

            data_min = df[col_data].min()
            data_max = df[col_data].max()

            filtro_data = st.date_input(
                "Período",
                value=(data_min, data_max)
            )
        else:
            filtro_data = None

    # ==============================
    # 🎯 APLICAÇÃO DOS FILTROS
    # ==============================
    df_filtrado = df.copy()

    if filtro_convenio:
        df_filtrado = df_filtrado[df_filtrado["CONVENIO"].isin(filtro_convenio)]

    if filtro_data and col_data:
        inicio, fim = filtro_data
        df_filtrado = df_filtrado[
            (df_filtrado[col_data] >= pd.to_datetime(inicio)) &
            (df_filtrado[col_data] <= pd.to_datetime(fim))
        ]

    return df_filtrado

def render_relatorio(nome_relatorio, pasta_relatorio):

    st.markdown(f'<div class="relatorio-titulo">{nome_relatorio}</div>', unsafe_allow_html=True)

    ultima = obter_ultima_atualizacao(pasta_relatorio)

    if ultima:
        st.markdown(f'<div class="relatorio-subtitulo">Última atualização: {ultima}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="relatorio-subtitulo">Aguardando upload</div>', unsafe_allow_html=True)

    # ==============================
    # 🔒 UPLOAD
    # ==============================
    with st.container():
        st.markdown('<div class="caixa-upload">', unsafe_allow_html=True)
        st.subheader("Upload da planilha")

        if admin:
            uploaded_file = st.file_uploader(
                f"Upload - {nome_relatorio}",
                type=["xlsx", "xls"],
                key=pasta_relatorio
            )

            if st.button(f"Salvar {nome_relatorio}", key=f"btn_{pasta_relatorio}"):
                if uploaded_file:
                    salvar_upload_relatorio(uploaded_file, pasta_relatorio)
                    st.success("Upload realizado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Selecione um arquivo")
        else:
            st.info("Visualização disponível")

        st.markdown("</div>", unsafe_allow_html=True)

    # ==============================
    # 📥 DADOS
    # ==============================
    df = carregar_base_atual(pasta_relatorio)

    if df is None or df.empty:
        st.info("Nenhuma base carregada ainda.")
        return

    df = ajustar_header(df)

    # ==============================
    # 🔎 FILTROS
    # ==============================
    df_filtrado = aplicar_filtros(df)

    # ==============================
    # 📊 TABELA
    # ==============================
    st.markdown("---")

    st.data_editor(
        df_filtrado,
        width="stretch",
        hide_index=True,
        height=650,
        disabled=True
    )

    # ==============================
    # 📥 DOWNLOAD
    # ==============================
    excel = dataframe_to_excel_bytes(df_filtrado, pasta_relatorio)

    st.download_button(
        "📥 Baixar Excel",
        data=excel,
        file_name=f"{pasta_relatorio}.xlsx"
    )

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
        render_relatorio("CONTROLE DE DATAS", "controle_datas")

    elif opcao == "ASSERTIVIDADE FRONT":
        render_relatorio("ASSERTIVIDADE FRONT", "assertividade_front")

    elif opcao == "INADIMPLENCIA GERAL":
        render_relatorio("INADIMPLENCIA GERAL", "inadimplencia_geral")

    elif opcao == "INADIMPLENCIA 1º VENC":
        render_relatorio("INADIMPLENCIA 1º VENC", "inadimplencia_1venc")

    elif opcao == "INADIMPLENCIA ACIMA 5%":
        render_relatorio("INADIMPLENCIA ACIMA DE 5%", "inadimplencia_5")

    elif opcao == "TABELA GERAL POR CONSIGNATARIA":
        render_relatorio("TABELA GERAL POR CONSIGNATARIA", "tabela_consignataria")

if __name__ == "__main__":
    main()