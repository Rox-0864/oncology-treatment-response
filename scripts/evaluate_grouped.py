"""Evalúa el modelo con GroupKFold (agrupado por paciente) y, opcionalmente, SHAP.

Uso:
    python scripts/evaluate_grouped.py                     # GroupKFold sin SHAP
    python scripts/evaluate_grouped.py --shap              # + importancia SHAP
    python scripts/evaluate_grouped.py --model xgboost --shap
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from src.data.cleaning import clean
from src.data.loader import load_data
from src.modeling.group_eval import evaluate_grouped
from src.utils.logging import setup_logging


def main() -> int:
    p = argparse.ArgumentParser(description="Evaluación GroupKFold + SHAP")
    p.add_argument("--data", default="data/dataset.csv")
    p.add_argument(
        "--model",
        choices=["random_forest", "gradient_boosting", "logistic", "decision_tree", "xgboost"],
        default="random_forest",
    )
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--shap", action="store_true", help="calcular importancia SHAP")
    return _run(p.parse_args())


def _run(args) -> int:
    cfg = Config(data_path=args.data, model_name=args.model)
    setup_logging("logs")

    df = load_data(cfg.data_path, cfg.encoding)
    df = clean(df, cfg.response_col, cfg.numeric_cols)
    df = df.dropna(subset=[cfg.response_binary_col]).copy()

    summary = evaluate_grouped(
        df, cfg, n_splits=args.folds, use_shap=args.shap, results_dir=cfg.results_dir
    )

    os.makedirs(cfg.results_dir, exist_ok=True)
    with open(os.path.join(cfg.results_dir, "grouped_metrics.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n=== Evaluación GroupKFold (por PACIENTE) ===")
    for k, v in summary.items():
        if not k.startswith("shap"):
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
