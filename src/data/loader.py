"""Carga del dataset desde CSV o Excel.

El dataset que se entrega en ``data/dataset.csv`` YA está des-identificado
(ver ``src/data/deidentify.py``). Esta función es el punto único de entrada
para leerlo, de forma portable y sin rutas absolutas.
"""

from __future__ import annotations

import pandas as pd


def load_data(path: str, encoding: str = "utf-8", sheet_name: str | None = None) -> pd.DataFrame:
    """Carga un CSV o XLSX en un DataFrame.

    Args:
        path: ruta del archivo (relativa a la raíz del repo).
        encoding: codificación (utf-8 para los datos ya normalizados;
            latin-1 para archivos heredados del proyecto original).
        sheet_name: hoja a leer si es un Excel.
    """
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path, sheet_name=sheet_name)
    return pd.read_csv(path, encoding=encoding)
