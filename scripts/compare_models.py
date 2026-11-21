"""Compara los modelos disponibles y explora el umbral de decisión.

Métrica principal: AUC-ROC. Además reporta recall/precision/F1 de la clase
minoritaria (progresión), que es la que importa clínicamente, y el mejor umbral
(Youden) para ver cuánta sensibilidad se puede recuperar.

Uso:
    python scripts/compare_models.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar el script desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

from config import Config
from src.data.cleaning import clean
from src.data.loader import load_data
from src.modeling.train import MODEL_FACTORIES, build_pipeline


def best_threshold_by_youden(y_true, y_prob) -> float:
    """Umbral que maximiza el índice de Youden (tpr - fpr)."""
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    j = tpr - fpr
    idx = int(np.argmax(j))
    # thresholds tiene len(tpr) - 1 elementos
    idx = min(idx, len(thresholds) - 1)
    return float(thresholds[idx])


def main() -> int:
    cfg = Config()
    df = load_data(cfg.data_path, cfg.encoding)
    df = clean(df, cfg.response_col, cfg.numeric_cols)
    df = df.dropna(subset=[cfg.response_binary_col]).copy()
    df[cfg.response_binary_col] = df[cfg.response_binary_col].astype(int)

    cat = [c for c in cfg.categorical_cols if c in df.columns]
    num = [c for c in cfg.numeric_cols if c in df.columns]
    X = df[cat + num]
    y = df[cfg.response_binary_col]

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=cfg.test_size, random_state=cfg.random_state, stratify=y
    )

    print(f"{'modelo':20s} {'AUC':>6s} {'acc':>6s} {'rec0':>6s} {'prec0':>6s} "
          f"{'rec0*':>6s} {'umbral*':>8s}")
    print("-" * 70)

    for name in MODEL_FACTORIES:
        pipe = build_pipeline(name, cat, num, use_smote=True, random_state=cfg.random_state)
        pipe.fit(Xtr, ytr)
        y_prob = pipe.predict_proba(Xte)[:, 1]
        y_pred = pipe.predict(Xte)

        auc = roc_auc_score(yte, y_prob)
        acc = accuracy_score(yte, y_pred)
        rep = classification_report(yte, y_pred, output_dict=True)
        rec0 = rep["0"]["recall"]
        prec0 = rep["0"]["precision"]

        # Umbral óptimo (Youden) y recall de la clase 0 en ese umbral.
        thr = best_threshold_by_youden(yte, y_prob)
        y_pred_t = (y_prob >= thr).astype(int)
        rep_t = classification_report(yte, y_pred_t, output_dict=True)
        rec0_t = rep_t["0"]["recall"]

        print(f"{name:20s} {auc:6.3f} {acc:6.3f} {rec0:6.2f} {prec0:6.2f} "
              f"{rec0_t:6.2f} {thr:8.3f}")

    print("\nrec0  = recall de 'progresión' (clase 0) al umbral por defecto 0.5")
    print("rec0* = recall de 'progresión' al umbral óptimo (Youden)")
    print("Nota: con solo ~16 casos de progresión, estos números son muy ruidosos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
