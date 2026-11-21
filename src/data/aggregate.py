"""Agregación a nivel de PACIENTE.

El dataset tiene 466 tumores de 97 pacientes. Agrupar por paciente produce una
fila por paciente, con métricas agregadas de sus tumores. Es el análisis
clínicamente correcto: la unidad de observación es el paciente, no el tumor.

Respuesta agregada: ``min`` de las respuestas por tumor. Como ``0`` = fracaso
(progresión), el paciente se considera "fracaso" si CUALQUIERA de sus tumores
progresó; "éxito" solo si todos se controlaron.
"""

from __future__ import annotations

import pandas as pd


def _mode(x: pd.Series):
    """Moda robusta (ignora NaN)."""
    vals = x.dropna()
    if vals.empty:
        return None
    m = vals.mode()
    return m.iloc[0]


# Columnas constantes por paciente (se toma la primera).
_FIRST_COLS = [
    "EDAD", "SEXO", "TUMOR PRIMARIO", "SUBTIPO HISTOLOGICO",
    "PERFIL MOLECULAR", "AÑO",
]

# Columnas de tratamiento (pueden variar por tumor; se toma la moda).
_MODE_COLS = ["CIRUGIA PREVIA", "SRS", "TECNICA", "TRATAMIENTO SISTEMICO"]

# Features del dataset AGREGADO (una fila por paciente).
AGG_CATEGORICAL_COLS = [
    "SEXO", "TUMOR PRIMARIO", "SUBTIPO HISTOLOGICO", "PERFIL MOLECULAR",
    "CIRUGIA PREVIA", "SRS", "TECNICA", "TRATAMIENTO SISTEMICO",
]
AGG_NUMERIC_COLS = [
    "EDAD", "AÑO", "NUM_TUMORES", "TAMAÑO_MEAN", "NUM_LOCALIZACIONES", "DOSIS_MEAN",
]


def aggregate_by_patient(df: pd.DataFrame, patient_id_col: str, response_col: str) -> pd.DataFrame:
    """Devuelve un DataFrame con una fila por paciente.

    Args:
        df: dataset limpio y des-identificado.
        patient_id_col: columna identificadora (``PACIENTE``).
        response_col: columna de respuesta binaria (``RESPUESTA_BINARIA``).
    """
    agg_spec: dict[str, tuple] = {}

    for c in _FIRST_COLS:
        if c in df.columns:
            agg_spec[c] = (c, "first")
    for c in _MODE_COLS:
        if c in df.columns:
            agg_spec[c] = (c, _mode)

    if "No. METS" in df.columns:
        agg_spec["NUM_TUMORES"] = ("No. METS", "max")
    if "TAMAÑO (mm)" in df.columns:
        agg_spec["TAMAÑO_MEAN"] = ("TAMAÑO (mm)", "mean")
    if "LOCALIZACION" in df.columns:
        agg_spec["NUM_LOCALIZACIONES"] = ("LOCALIZACION", "nunique")
    if "DOSIS (Gy)" in df.columns:
        agg_spec["DOSIS_MEAN"] = ("DOSIS (Gy)", "mean")

    # Respuesta: fracaso si CUALQUIER tumor progresó (min, porque 0 = fracaso).
    if response_col in df.columns:
        agg_spec[response_col] = (response_col, "min")

    agg = df.groupby(patient_id_col).agg(**agg_spec).reset_index()
    return agg
