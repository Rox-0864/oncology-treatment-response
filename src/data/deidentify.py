"""Des-identificación de datos de pacientes.

El dataset original contenía el número de historia clínica (``EXPEDIENTE``),
un identificador directo que NO debe publicarse. Este módulo lo reemplaza por
un identificador pseudoanonimizado irreversible (``PACIENTE``), derivado de un
hash SHA-256 con una *salt* privada.

Uso típico (sobre el Excel/csv crudo, ANTES de commitear nada)::

    df = load_data("data/raw/NoContry.xlsx", sheet_name="PX INCLUIDOS")
    df = deidentify(df, id_col="EXPEDIENTE", drop_cols=("EXPEDIENTE", "NOMBRE", "ID_unico"))
"""

from __future__ import annotations

import hashlib
import os
from typing import Iterable

import pandas as pd

# Salt privada. Se lee de la variable de entorno si existe; en producción
# conviene que sea secreta (no commitearla junto a los datos).
_DEFAULT_SALT = "neurotx-deident-2026"


def _salt() -> str:
    return os.environ.get("NEUROTX_DEIDENT_SALT", _DEFAULT_SALT)


def surrogate_id(values: pd.Series) -> pd.Series:
    """Convierte una serie de identificadores en IDs pseudoanonimizados."""
    salt = _salt()
    return values.astype(str).map(
        lambda x: "PT-" + hashlib.sha256((salt + x).encode("utf-8")).hexdigest()[:10]
    )


def deidentify(
    df: pd.DataFrame,
    id_col: str,
    drop_cols: Iterable[str] = (),
) -> pd.DataFrame:
    """Reemplaza ``id_col`` por un ``PACIENTE`` pseudoanonimizado y elimina el resto.

    Args:
        df: DataFrame con los datos crudos.
        id_col: columna identificadora del paciente (p. ej. ``EXPEDIENTE``).
        drop_cols: otras columnas a eliminar (``NOMBRE``, ``ID_unico``, ...).

    Returns:
        DataFrame sin identificadores directos.
    """
    df = df.copy()

    # 1) Pseudoanonimizar el identificador (conserva la agrupación por paciente).
    df["PACIENTE"] = surrogate_id(df[id_col])

    # 2) Eliminar identificadores directos y por-fila.
    to_drop = {id_col, *drop_cols}
    df = df.drop(columns=[c for c in to_drop if c in df.columns], errors="ignore")

    # 3) Reordenar PACIENTE al inicio.
    cols = ["PACIENTE"] + [c for c in df.columns if c != "PACIENTE"]
    return df[cols]
