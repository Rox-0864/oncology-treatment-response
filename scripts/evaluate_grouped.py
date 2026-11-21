"""Evalúa el modelo de forma honesta: GroupKFold, agregación por paciente, SHAP
y validación anidada.

Uso:
    python scripts/evaluate_grouped.py                     # GroupKFold por paciente
    python scripts/evaluate_grouped.py --shap              # + importancia SHAP
    python scripts/evaluate_grouped.py --aggregate         # una fila por paciente
    python scripts/evaluate_grouped.py --nested            # validación anidada (tuning)
    python scripts/evaluate_grouped.py --model xgboost --nested --aggregate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from src.data.aggregate import AGG_CATEGORICAL_COLS, AGG_NUMERIC_COLS, aggregate_by_patient
from src.data.cleaning import clean
from src.data.loader import load_data
from src.modeling.group_eval import evaluate_grouped, nested_cv_evaluate
from src.utils.logging import setup_logging


def main() -> int:
    p = argparse.ArgumentParser(description="Evaluación GroupKFold + SHAP + anidada")
    p.add_argument("--data", default="data/dataset.csv")
    p.add_argument(
        "--model",
        choices=["random_forest", "gradient_boosting", "logistic", "decision_tree", "xgboost"],
        default="random_forest",
    )
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--shap", action="store_true", help="calcular importancia SHAP")
    p.add_argument("--aggregate", action="store_true", help="agregar a nivel de paciente")
    p.add_argument("--nested", action="store_true", help="validación anidada con tuning")
    return _run(p.parse_args())


def _run(args) -> int:
    cfg = Config(data_path=args.data, model_name=args.model)
    setup_logging("logs")

    df = load_data(cfg.data_path, cfg.encoding)
    df = clean(df, cfg.response_col, cfg.numeric_cols)
    df = df.dropna(subset=[cfg.response_binary_col]).copy()
    df[cfg.response_binary_col] = df[cfg.response_binary_col].astype(int)

    cat_cols, num_cols = list(cfg.categorical_cols), list(cfg.numeric_cols)
    modo = "nivel tumor"
    if args.aggregate:
        df = aggregate_by_patient(df, cfg.patient_id_col, cfg.response_binary_col)
        cat_cols, num_cols = list(AGG_CATEGORICAL_COLS), list(AGG_NUMERIC_COLS)
        modo = "nivel paciente"

    print(f"\n=== Evaluación {modo} ({len(df)} filas, {df[cfg.patient_id_col].nunique()} pacientes) ===")
    print(f"Distribución de clases: {dict(df[cfg.response_binary_col].value_counts().sort_index())}")

    if args.nested:
        summary = nested_cv_evaluate(
            df, cfg, n_splits=args.folds, results_dir=cfg.results_dir,
            cat_cols=cat_cols, num_cols=num_cols,
        )
    else:
        summary = evaluate_grouped(
            df, cfg, n_splits=args.folds, use_shap=args.shap, results_dir=cfg.results_dir,
            cat_cols=cat_cols, num_cols=num_cols,
        )

    os.makedirs(cfg.results_dir, exist_ok=True)
    fname = "grouped_metrics.json" if not args.nested else "nested_metrics.json"
    with open(os.path.join(cfg.results_dir, fname), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    for k, v in summary.items():
        if not k.startswith("shap") and k != "mejores_hiperparametros_por_fold":
            print(f"  {k}: {v}")
    if "mejores_hiperparametros_por_fold" in summary:
        print("  mejores_hiperparametros_por_fold:")
        for i, bp in enumerate(summary["mejores_hiperparametros_por_fold"]):
            print(f"    fold {i}: {bp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
