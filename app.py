import streamlit as st
import pandas as pd
import unicodedata

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
            }
            .relatorio-subtitulo {
                color: #6b7280;
                font-size: 0.9rem;
                margin-bottom: 1rem;
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
# 🔤 NORMALIZAR TEXTO (REMOVE ACENTO)
# ==============================
def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("utf-8")
    return texto.upper().strip()

# ==============================
# 🧠 AJUSTAR ESTRUTURA
# ==============================
def ajustar_estrutura(df):

    def normalizar(texto):
        if pd.isna(texto):
            return ""
        texto = str(texto)
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ASCII", "ignore").decode("utf-8")
        return texto.upper().strip()

    header_index = None

    # 🔍 encontrar linha do cabeçalho real
    for i, row in df.iterrows():
        valores = [normalizar(x) for x in row.values]
        if any("CONVENIO" in v for v in valores):
            header_index = i
            break

    if header_index is None:
        st.warning("⚠️ Cabeçalho não encontrado")
        return df

    header_1 = df.iloc[header_index - 1] if header_index > 0 else None
    header_2 = df.iloc[header_index]

    colunas = []

    for i in range(len(header_2)):
        h1 = normalizar(header_1[i]) if header_1 is not None else ""
        h2 = normalizar(header_2[i])

        if h1 and h2:
            nome = f"{h1}_{h2}"
        elif h2:
            nome = h2
        else:
            nome = h1

        colunas.append(nome)

    df.columns = colunas

    # remover headers
    df = df.iloc[header_index + 1:].reset_index(drop=True)

    # limpeza final
    df = limpar_df(df)

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

def limpar_df(df):

    # remover linhas e colunas totalmente vazias
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")

    # remover colunas lixo
    df = df.loc[:, ~df.columns.astype(str).str.contains("UNNAMED|NONE|NAN", case=False)]

    # limpar nomes
    df.columns = [str(col).strip() for col in df.columns]

    return df

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
# 🎨 FORMATAR DADOS
# ==============================
def formatar_dados(df):

    for col in df.columns:

        nome = col.upper()

        # 💰 MOEDA
        if any(x in nome for x in ["VALOR", "PMT", "INADIMPL"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                if pd.notnull(x) else ""
            )

        # 📊 PORCENTAGEM
        elif "%" in nome or "PERCENT" in nome:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].apply(
                lambda x: f"{x:.2%}".replace(".", ",")
                if pd.notnull(x) else ""
            )

        # ⏱ SLA
        elif "SLA" in nome:
            df[col] = df[col].astype(str)
            df[col] = df[col].str.replace("dia(s)", "d")
            df[col] = df[col].str.replace("hora(s)", "h")
            df[col] = df[col].str.replace("minutos", "m")
            df[col] = df[col].str.replace("e", "")
            df[col] = df[col].str.strip()

    return df

# ==============================
# 🔎 FILTROS
# ==============================
def aplicar_filtros(df):

    st.markdown("### 🔎 Filtros")

    col1, col2 = st.columns(2)

    # identificar coluna de data
    col_data = None
    for col in df.columns:
        if "DATA" in col.upper() or "CHEGADA" in col.upper():
            col_data = col
            break

    # convênio
    with col1:
        if "CONVENIO" in df.columns:
            lista = sorted(df["CONVENIO"].dropna().unique())
            filtro_convenio = st.multiselect("Convênio", lista)
        else:
            filtro_convenio = []

    # data
    with col2:
        if col_data:
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
            datas_validas = df[col_data].dropna()

            if not datas_validas.empty:
                filtro_data = st.date_input(
                    "Período",
                    value=(datas_validas.min(), datas_validas.max())
                )
            else:
                filtro_data = None
        else:
            filtro_data = None

    # aplicar
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

# ==============================
# 📊 RENDER PADRÃO
# ==============================
def render_relatorio(nome_relatorio, pasta_relatorio):

    st.markdown(f'<div class="relatorio-titulo">{nome_relatorio}</div>', unsafe_allow_html=True)

    ultima = obter_ultima_atualizacao(pasta_relatorio)

    if ultima:
        st.markdown(f'<div class="relatorio-subtitulo">Última atualização: {ultima}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="relatorio-subtitulo">Aguardando upload</div>', unsafe_allow_html=True)

    # UPLOAD
    with st.container():
        st.markdown('<div class="caixa-upload">', unsafe_allow_html=True)

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

    # DADOS
    df = carregar_base_atual(pasta_relatorio)

    if df is None or df.empty:
        st.info("Nenhuma base carregada ainda.")
        return

    df = ajustar_estrutura(df)

    # 🔎 FILTROS PRIMEIRO
    df_filtrado = aplicar_filtros(df)

    # 🎨 FORMATAR DEPOIS
    df_filtrado = formatar_dados(df_filtrado)

    # TABELA
    st.markdown("---")

    st.data_editor(
        df_filtrado,
        width="stretch",
        hide_index=True,
        height=650,
        disabled=True
    )

    # DOWNLOAD
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