"""Evaluación honesta con GroupKFold (agrupada por PACIENTE) + SHAP.

El split aleatorio por fila del pipeline principal ignora que los tumores de un
mismo paciente están correlacionados (466 tumores de 97 pacientes). GroupKFold
separa por ``PACIENTE``, evitando que un mismo paciente aparezca en train y test
al mismo tiempo (fuga de datos).

SHAP (opcional) explica *por qué* el modelo decide, lo que es clave para que un
clínico confíe en la herramienta.
"""

from __future__ import annotations

import logging
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

from src.modeling.train import build_pipeline  # noqa: E402

logger = logging.getLogger(__name__)


def evaluate_grouped(
    df: pd.DataFrame,
    cfg,
    n_splits: int = 5,
    use_shap: bool = False,
    results_dir: str = "results",
) -> dict:
    """Evalúa el modelo con GroupKFold (por paciente) y devuelve métricas medias.

    Se omiten los folds de test donde no están presentes ambas clases (con 16
    casos de progresión puede ocurrir).
    """
    os.makedirs(results_dir, exist_ok=True)

    cat = [c for c in cfg.categorical_cols if c in df.columns]
    num = [c for c in cfg.numeric_cols if c in df.columns]
    X = df[cat + num]
    y = df[cfg.response_binary_col].astype(int)
    groups = df[cfg.patient_id_col]

    gkf = GroupKFold(n_splits=n_splits)
    aucs, accs, rec0s, prec0s = [], [], [], []

    for fold, (tr_idx, te_idx) in enumerate(gkf.split(X, y, groups)):
        Xtr, Xte = X.iloc[tr_idx], X.iloc[te_idx]
        ytr, yte = y.iloc[tr_idx], y.iloc[te_idx]

        if len(set(yte)) < 2:
            logger.warning("Fold %d sin ambas clases: se omite.", fold)
            continue

        pipe = build_pipeline(
            cfg.model_name, cat, num,
            use_smote=cfg.use_smote, random_state=cfg.random_state,
        )
        pipe.fit(Xtr, ytr)
        y_prob = pipe.predict_proba(Xte)[:, 1]
        y_pred = pipe.predict(Xte)

        aucs.append(roc_auc_score(yte, y_prob))
        accs.append(accuracy_score(yte, y_pred))
        rep = classification_report(yte, y_pred, output_dict=True, zero_division=0)
        rec0s.append(rep["0"]["recall"])
        prec0s.append(rep["0"]["precision"])
        logger.info(
            "Fold %d: AUC=%.3f recall(progresión)=%.2f", fold, aucs[-1], rec0s[-1]
        )

    summary = {
        "model": cfg.model_name,
        "grouped_by": cfg.patient_id_col,
        "n_folds_validos": len(aucs),
        "auc_mean": float(np.mean(aucs)),
        "auc_std": float(np.std(aucs)),
        "accuracy_mean": float(np.mean(accs)),
        "recall_progresion_mean": float(np.mean(rec0s)),
        "precision_progresion_mean": float(np.mean(prec0s)),
    }

    if use_shap:
        pipe_full = build_pipeline(
            cfg.model_name, cat, num, use_smote=cfg.use_smote, random_state=cfg.random_state
        )
        pipe_full.fit(X, y)
        imp = shap_importance(pipe_full, X, results_dir)
        summary["shap_top_features"] = imp.head(10).to_dict()

    return summary


def shap_importance(pipe_fitted, X: pd.DataFrame, results_dir: str) -> pd.Series:
    """Calcula la importancia SHAP (mean |SHAP|) de un pipeline ya ajustado."""
    import shap

    prep = pipe_fitted.named_steps["prep"]
    model = pipe_fitted.named_steps["model"]
    names = prep.get_feature_names_out()

    Xt = prep.transform(X)
    # OneHotEncoder puede devolver una matriz dispersa; SHAP y el slicing
    # son más simples con un array denso (el dataset es chico).
    if hasattr(Xt, "toarray"):
        Xt = Xt.toarray()
    sample = Xt[: min(400, Xt.shape[0])]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)

    # Normalizar la salida según la versión/modelo:
    #  - lista de arrays por clase (algunas versiones)
    #  - array 2D (n_samples, n_features)
    #  - array 3D (n_samples, n_features, n_classes)
    sv = shap_values
    if isinstance(sv, list):
        sv = sv[1] if len(sv) > 1 else sv[0]
    sv = np.asarray(sv)
    if sv.ndim == 3:
        sv = sv[:, :, -1]  # clase positiva (éxito)
    if hasattr(sv, "toarray"):
        sv = sv.toarray()

    imp = pd.Series(np.abs(sv).mean(axis=0), index=names).sort_values(ascending=False)
    imp.to_csv(os.path.join(results_dir, "shap_importance.csv"))

    top = imp.head(15)
    plt.figure(figsize=(8, 7))
    plt.barh(top.index[::-1], top.values[::-1])
    plt.title("Importancia SHAP (mean |SHAP|)")
    plt.xlabel("mean |SHAP value|")
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "shap_importance.png"), dpi=150)
    plt.close()

    logger.info("Top features SHAP:\n%s", top.to_string())
    return imp
