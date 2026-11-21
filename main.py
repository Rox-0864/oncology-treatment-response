"""Punto de entrada del pipeline: limpiar, analizar y entrenar.

Ejecutar desde la raíz del repositorio:

    python main.py                     # pipeline completo (Random Forest)
    python main.py --model xgboost    # otro modelo
    python main.py --stats            # incluye pruebas estadísticas
    python main.py --help
"""

from __future__ import annotations

import argparse
import logging
import random

import numpy as np

from config import Config
from src.analysis import stats
from src.data.cleaning import clean
from src.data.loader import load_data
from src.modeling.train import train_and_evaluate
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Análisis y predicción de respuesta oncológica")
    p.add_argument("--data", default="data/dataset.csv")
    p.add_argument(
        "--model",
        choices=["random_forest", "gradient_boosting", "logistic", "decision_tree", "xgboost"],
        default="random_forest",
    )
    p.add_argument("--no-smote", action="store_true", help="desactivar el balanceo con SMOTE")
    p.add_argument("--stats", action="store_true", help="ejecutar las pruebas estadísticas")
    return p.parse_args()


def run_stats(df) -> None:
    """Ejecuta y registra las pruebas de asociación principales."""
    resp = "RESPUESTA_BINARIA"
    logger.info("=" * 60)
    logger.info("PRUEBAS ESTADÍSTICAS")
    for col in ["SRS", "CIRUGIA PREVIA", "TECNICA", "TUMOR PRIMARIO", "SEXO"]:
        if col in df.columns:
            r = stats.chi2_test(df, col, resp)
            logger.info("chi2 %s vs %s: p=%.4f (chi2=%.2f)", col, resp, r["p_value"], r["chi2"])

    if "DOSIS (Gy)" in df.columns and "RESPUESTA (CRITERIOS RANO)" in df.columns:
        r = stats.anova_test(df, "DOSIS (Gy)", "RESPUESTA (CRITERIOS RANO)")
        logger.info("ANOVA DOSIS vs RESPUESTA: p=%.4f (F=%.2f)", r["p_value"], r["f_value"])
    logger.info("=" * 60)


def main() -> int:
    args = parse_args()
    cfg = Config(
        data_path=args.data,
        model_name=args.model,
        use_smote=not args.no_smote,
    )

    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    setup_logging(cfg.results_dir.replace("results", "logs"))

    # 1. Cargar y limpiar
    df = load_data(cfg.data_path, cfg.encoding)
    df = clean(df, cfg.response_col)
    logger.info("Dataset limpio: %d filas x %d columnas", df.shape[0], df.shape[1])

    # 2. Análisis estadístico (opcional)
    if args.stats:
        run_stats(df)

    # 3. Entrenar y evaluar
    result = train_and_evaluate(df, cfg)
    logger.info("Pipeline finalizado. Métricas: %s", result["metrics"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
