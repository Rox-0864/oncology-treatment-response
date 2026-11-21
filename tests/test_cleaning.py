"""Tests de limpieza (no requieren el dataset real)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data.cleaning import clean_tamano, map_response_binary


def test_map_response_binary_correct_mapping():
    df = pd.DataFrame(
        {
            "RANO": [
                "RESPUESTA COMPLETA",
                "RESPUESTA PARCIAL",
                "ESTABLE",
                "PROGRESION",
                "PROGRESIÓN",
            ]
        }
    )
    out = map_response_binary(df, "RANO")
    assert list(out["RESPUESTA_BINARIA"]) == [1, 1, 1, 0, 0]


def test_map_response_unknown_is_nan():
    df = pd.DataFrame({"RANO": ["ALGO DESCONOCIDO", np.nan]})
    out = map_response_binary(df, "RANO")
    assert out["RESPUESTA_BINARIA"].isna().all()


def test_clean_tamano():
    df = pd.DataFrame({"TAMAÑO (mm)": ["26", "4.55", "20240611000000", "abc", ""]})
    out = clean_tamano(df)
    assert out["TAMAÑO (mm)"].iloc[0] == 26.0
    assert out["TAMAÑO (mm)"].iloc[1] == 4.55
    assert pd.isna(out["TAMAÑO (mm)"].iloc[2])  # valor corrupto -> NaN
    assert pd.isna(out["TAMAÑO (mm)"].iloc[3])
    assert pd.isna(out["TAMAÑO (mm)"].iloc[4])
