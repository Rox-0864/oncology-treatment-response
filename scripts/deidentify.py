"""Des-identifica un dataset crudo (con ``EXPEDIENTE``) y lo guarda en formato limpio.

Ejecutar ANTES de commitear cualquier dato, sobre la copia cruda que NO va a git:

    python scripts/deidentify.py --input "data/raw/NoContry.xlsx" --sheet "PX INCLUIDOS"

El archivo crudo debe estar en ``data/raw/`` (carpeta ignorada por git).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Permite ejecutar el script desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.deidentify import deidentify
from src.data.loader import load_data


def main() -> int:
    p = argparse.ArgumentParser(description="Des-identifica el dataset crudo")
    p.add_argument("--input", required=True, help="ruta del CSV/XLSX crudo")
    p.add_argument("--sheet", default=None, help="hoja del Excel (si aplica)")
    p.add_argument("--id-col", default="EXPEDIENTE", help="columna identificadora")
    p.add_argument("--output", default="data/dataset.csv")
    args = p.parse_args()

    df = load_data(args.input, encoding="latin-1", sheet_name=args.sheet)
    df = deidentify(df, id_col=args.id_col, drop_cols=("NOMBRE", "ID_unico"))

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8")
    print(f"Dataset des-identificado guardado en {args.output} ({len(df)} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
