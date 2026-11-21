"""Limpieza y normalización de los datos clínicos.

Cada función es pura (recibe un DataFrame y devuelve otro), por lo que es
testeable sin necesidad del dataset real.

Correcciones que aplica (tomadas de los notebooks originales, ya depuradas):
- Normaliza nombres de columna (espacios y acentos no controlados).
- Limpia ``TAMAÑO (mm)``: deja solo dígitos, vacíos -> NaN y corrige un valor
  corrupto ('20240611000000') que rompía la conversión a float.
- Normaliza valores de ``LOCALIZACION`` (sinónimos).
- Elimina categorías inválidas de ``SRS`` ('CONV', 'Unknown').
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

# Valores que se consideran "éxito" (control de la enfermedad) según RANO.
# NOTA: "ESTABLE" se considera éxito (sin progresión). El notebook original
# ``analisisROX.ipynb`` lo mapeaba como fracaso (0), lo que era un bug: el
# dataset final sí lo cuenta como éxito (1).
SUCCESS_VALUES = {"RESPUESTA COMPLETA", "RESPUESTA PARCIAL", "ESTABLE"}
FAILURE_VALUES = {"PROGRESION", "PROGRESIÓN"}

# Sinónimos de localización observados en los datos (normalización).
LOCALIZACION_REPLACEMENTS = {
    "PARIETAL IZQ": "PARIETAL IZQUIERDA",
    "ORBITARIA IZQUIERDA": "ORBITA IZQUIERDA",
    "CEERBELO": "CEREBELO",
    "CEREBELO ": "CEREBELO",
    "ÓRBITA IZQUIERDA": "ORBITA IZQUIERDA",
}


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Quita espacios al inicio/final de los nombres de columna."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def map_response_binary(df: pd.DataFrame, response_col: str) -> pd.DataFrame:
    """Deriva la respuesta binaria (1 = éxito, 0 = progresión) desde RANO.

    Usa el mapeo correcto: éxito = respuesta completa, parcial o estable
    (control de enfermedad); fracaso = progresión.
    """
    df = df.copy()

    def _map(v):
        if pd.isna(v):
            return np.nan
        s = str(v).strip().upper()
        if s in SUCCESS_VALUES:
            return 1
        if s in FAILURE_VALUES:
            return 0
        return np.nan  # valor desconocido: no asumir éxito ni fracaso

    df["RESPUESTA_BINARIA"] = df[response_col].map(_map)
    return df


def clean_tamano(df: pd.DataFrame, col: str = "TAMAÑO (mm)") -> pd.DataFrame:
    """Limpia la columna de tamaño: deja solo dígitos y la convierte a float."""
    df = df.copy()
    # 1) Quitar todo lo que no sea dígito o punto.
    df[col] = df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
    # 2) Vacíos -> NaN.
    df[col] = df[col].replace("", np.nan)
    # 3) Valor corrupto observado (fecha sin separadores).
    df[col] = df[col].replace("20240611000000", np.nan)
    # 4) Convertir a float (errores -> NaN).
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_localizacion(df: pd.DataFrame, col: str = "LOCALIZACION") -> pd.DataFrame:
    """Normaliza sinónimos de localización."""
    df = df.copy()
    df[col] = df[col].replace(LOCALIZACION_REPLACEMENTS)
    return df


def drop_invalid_srs(
    df: pd.DataFrame, col: str = "SRS", invalid: tuple = ("CONV", "Unknown")
) -> pd.DataFrame:
    """Elimina filas con categorías inválidas de tratamiento SRS."""
    df = df.copy()
    mask = df[col].isin(invalid)
    if mask.any():
        df = df[~mask].reset_index(drop=True)
    return df


def coerce_numeric(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Convierte columnas numéricas a float, dejando NaN donde no se pueda.

    Corrige valores como 'MULTIPLES' en ``No. METS`` o 'Unknown' en
    ``TAMAÑO (mm)``, que rompían el imputer numérico.
    """
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean(df: pd.DataFrame, response_col: str, numeric_cols: tuple = ()) -> pd.DataFrame:
    """Aplica la secuencia completa de limpieza."""
    df = normalize_column_names(df)
    df = map_response_binary(df, response_col)
    df = clean_tamano(df)
    df = clean_localizacion(df)
    df = drop_invalid_srs(df)
    df = coerce_numeric(df, numeric_cols)
    return df
