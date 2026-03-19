from pathlib import Path
from datetime import datetime
import pandas as pd


def _garantir_pasta_relatorio(pasta_relatorio: str) -> Path:
    base_dir = Path("data") / pasta_relatorio
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def salvar_upload_relatorio(uploaded_file, pasta_relatorio: str) -> str:
    base_dir = _garantir_pasta_relatorio(pasta_relatorio)

    extensao = Path(uploaded_file.name).suffix.lower()
    if extensao not in [".xlsx", ".xls"]:
        extensao = ".xlsx"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    historico_path = base_dir / f"{timestamp}{extensao}"
    latest_path = base_dir / f"latest{extensao}"

    conteudo = uploaded_file.getbuffer()

    with open(historico_path, "wb") as f:
        f.write(conteudo)

    with open(latest_path, "wb") as f:
        f.write(conteudo)

    arquivo_oposto = base_dir / ("latest.xls" if extensao == ".xlsx" else "latest.xlsx")
    if arquivo_oposto.exists():
        arquivo_oposto.unlink()

    return str(latest_path)


def carregar_base_atual(pasta_relatorio: str):
    base_dir = _garantir_pasta_relatorio(pasta_relatorio)

    arquivo_xlsx = base_dir / "latest.xlsx"
    arquivo_xls = base_dir / "latest.xls"

    try:
        if arquivo_xlsx.exists():
            return pd.read_excel(arquivo_xlsx)
        if arquivo_xls.exists():
            return pd.read_excel(arquivo_xls)
    except Exception:
        return None

    return None


def obter_ultima_atualizacao(pasta_relatorio: str):
    base_dir = _garantir_pasta_relatorio(pasta_relatorio)

    arquivo_xlsx = base_dir / "latest.xlsx"
    arquivo_xls = base_dir / "latest.xls"

    arquivo = None
    if arquivo_xlsx.exists():
        arquivo = arquivo_xlsx
    elif arquivo_xls.exists():
        arquivo = arquivo_xls

    if arquivo is None:
        return None

    data_mod = datetime.fromtimestamp(arquivo.stat().st_mtime)
    return data_mod.strftime("%d/%m/%Y %H:%M:%S")


def listar_historico_relatorio(pasta_relatorio: str):
    base_dir = _garantir_pasta_relatorio(pasta_relatorio)

    arquivos = []
    for arq in base_dir.iterdir():
        if arq.is_file() and arq.name not in ["latest.xlsx", "latest.xls"]:
            arquivos.append(arq.name)

    return sorted(arquivos, reverse=True)