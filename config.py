"""Configuración central del pipeline de análisis oncológico.

Todos los parámetros viven acá, en una única ``dataclass``, en lugar de estar
dispersos en celdas de notebook (uno de los problemas del proyecto original).

El dataset se entrega DES-IDENTIFICADO (ver ``src/data/deidentify.py``): no
contiene ``EXPEDIENTE`` ni ``NOMBRE``, solo un ``PACIENTE`` pseudoanonimizado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    # ------------------------------------------------------------------ Datos
    data_path: str = "data/dataset.csv"   # dataset ya des-identificado
    encoding: str = "utf-8"

    # Columna con el identificador pseudoanonimizado del paciente.
    patient_id_col: str = "PACIENTE"

    # Columna objetivo y su versión binaria.
    response_col: str = "RESPUESTA (CRITERIOS RANO)"
    response_binary_col: str = "RESPUESTA_BINARIA"

    # Columnas que se tratan como categóricas (se one-hot encodean).
    categorical_cols: Tuple[str, ...] = (
        "SEXO",
        "TUMOR PRIMARIO",
        "SUBTIPO HISTOLOGICO",
        "PERFIL MOLECULAR",
        "LOCALIZACION",
        "CIRUGIA PREVIA",
        "SRS",
        "TECNICA",
        "TRATAMIENTO SISTEMICO",
    )
    # Columnas numéricas.
    numeric_cols: Tuple[str, ...] = (
        "EDAD",
        "AÑO",
        "No. METS",
        "TAMAÑO (mm)",
        "DOSIS (Gy)",
    )

    # --------------------------------------------------------- Modelado
    model_name: str = "random_forest"  # random_forest | gradient_boosting | logistic | decision_tree | xgboost
    test_size: float = 0.3
    random_state: int = 42
    use_smote: bool = True             # balancear la clase minoritaria

    # ------------------------------------------------------------- Salidas
    results_dir: str = "results"
    model_dir: str = "models"

    # ---------------------------------------------------- Reproducibilidad
    seed: int = 42
