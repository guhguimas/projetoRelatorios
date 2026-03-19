import io
import pandas as pd


def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Relatorio") -> bytes:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])

    return output.getvalue()