from pathlib import Path
from datetime import datetime
import pandas as pd


def salvar_upload_relatorio(uploaded_file, pasta_relatorio: str) -> str:
    """
    Salva o arquivo enviado em:
    - histórico com data/hora
    - latest.xlsx como versão atual
    """
    base_dir = Path("data") / pasta_relatorio
    base_dir.mkdir(parents=True, exist_ok=True)

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

    return str(latest_path)


def carregar_base_atual(pasta_relatorio: str):
    """
    Carrega a base mais recente salva na pasta do relatório.
    """
    base_dir = Path("data") / pasta_relatorio

    arquivo_xlsx = base_dir / "latest.xlsx"
    arquivo_xls = base_dir / "latest.xls"

    if arquivo_xlsx.exists():
        return pd.read_excel(arquivo_xlsx)

    if arquivo_xls.exists():
        return pd.read_excel(arquivo_xls)

    return None


def obter_ultima_atualizacao(pasta_relatorio: str) -> str | None:
    """
    Retorna a data/hora de modificação do arquivo latest.
    """
    base_dir = Path("data") / pasta_relatorio

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