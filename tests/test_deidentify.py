"""Tests de des-identificación.

Ejecutar con:
    python -m pytest tests/
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data.deidentify import deidentify, surrogate_id


def test_surrogate_id_is_deterministic():
    s = pd.Series(["209406", "209406", "225523"])
    out = surrogate_id(s)
    assert out.iloc[0] == out.iloc[1]          # mismo id -> mismo hash
    assert out.iloc[0] != out.iloc[2]          # distinto id -> distinto hash
    assert all(v.startswith("PT-") for v in out)


def test_deidentify_drops_identifiers():
    df = pd.DataFrame(
        {
            "EXPEDIENTE": [1, 2, 2],
            "NOMBRE": ["A", "B", "B"],
            "EDAD": [50, 60, 60],
        }
    )
    out = deidentify(df, id_col="EXPEDIENTE", drop_cols=("NOMBRE",))
    assert "EXPEDIENTE" not in out.columns
    assert "NOMBRE" not in out.columns
    assert "PACIENTE" in out.columns
    assert out["PACIENTE"].nunique() == 2
