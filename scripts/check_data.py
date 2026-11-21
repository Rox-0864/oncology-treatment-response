"""Verifica que el dataset des-identificado no contenga datos personales.

Uso:
    python scripts/check_data.py
"""

from __future__ import annotations

import csv
import os
import sys

DATA_PATH = "data/dataset.csv"

# Columnas que NUNCA deben estar presentes en un dataset des-identificado.
PII_COLUMNS = {"EXPEDIENTE", "NOMBRE", "ID_UNICO", "ID_unico"}

# Columnas esperadas (las del dataset clínico normalizado).
EXPECTED = {
    "PACIENTE", "EDAD", "SEXO", "TUMOR PRIMARIO", "SUBTIPO HISTOLOGICO",
    "PERFIL MOLECULAR", "LOCALIZACION", "CIRUGIA PREVIA", "SRS",
    "DOSIS (Gy)", "TECNICA", "TRATAMIENTO SISTEMICO",
    "RESPUESTA (CRITERIOS RANO)", "RESPUESTA_BINARIA",
}


def main() -> int:
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: no existe {DATA_PATH}")
        return 1

    with open(DATA_PATH, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        cols = set(reader.fieldnames)

    problems = []
    found_pii = cols & PII_COLUMNS
    if found_pii:
        problems.append(f"Columnas PII detectadas: {sorted(found_pii)}")

    missing = EXPECTED - cols
    if missing:
        problems.append(f"Columnas esperadas ausentes: {sorted(missing)}")

    if problems:
        for pr in problems:
            print(f"ERROR: {pr}")
        return 1

    print(f"OK: {DATA_PATH} está des-identificado y tiene las columnas esperadas.")
    print(f"Columnas: {len(cols)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
