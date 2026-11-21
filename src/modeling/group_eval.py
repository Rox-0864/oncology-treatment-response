"""Evaluación honesta agrupada por PACIENTE + SHAP + validación anidada.

El split aleatorio por fila del pipeline principal ignora que los tumores de un
mismo paciente están correlacionados (466 tumores de 97 pacientes). GroupKFold
separa por ``PACIENTE``, evitando que un mismo paciente aparezca en train y test
(fuga de datos).

Funciones:
- ``evaluate_grouped``: GroupKFold simple (por paciente).
- ``nested_cv_evaluate``: validación anidada (tuning de hiperparámetros dentro
  de cada fold, evaluado en el fold externo).
- ``shap_importance``: importancia SHAP (mean |SHAP|).
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
from sklearn.model_selection import GridSearchCV, GroupKFold  # noqa: E402

from src.modeling.train import build_pipeline  # noqa: E402

logger = logging.getLogger(__name__)

# Grillas pequeñas para la validación anidada (mantienen el costo bajo).
_DEFAULT_GRIDS = {
    "random_forest": {"model__n_estimators": [50, 150], "model__max_depth": [None, 5]},
    "xgboost": {
        "model__n_estimators": [50, 150],
        "model__max_depth": [3, 6],
        "model__learning_rate": [0.05, 0.1],
    },
    "gradient_boosting": {"model__n_estimators": [50, 150], "model__max_depth": [2, 4]},
    "logistic": {"model__C": [0.1, 1.0, 10.0]},
    "decision_tree": {"model__max_depth": [None, 3, 5]},
}


def _resolve_cols(cfg, df, cat_cols, num_cols):
    cat = [c for c in (cat_cols or cfg.categorical_cols) if c in df.columns]
    num = [c for c in (num_cols or cfg.numeric_cols) if c in df.columns]
    return cat, num


def evaluate_grouped(
    df: pd.DataFrame,
    cfg,
    n_splits: int = 5,
    use_shap: bool = False,
    results_dir: str = "results",
    cat_cols=None,
    num_cols=None,
) -> dict:
    """Evalúa con GroupKFold (por paciente) y devuelve métricas medias."""
    os.makedirs(results_dir, exist_ok=True)

    cat, num = _resolve_cols(cfg, df, cat_cols, num_cols)
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

        pipe = build_pipeline(cfg.model_name, cat, num,
                              use_smote=cfg.use_smote, random_state=cfg.random_state)
        pipe.fit(Xtr, ytr)
        y_prob = pipe.predict_proba(Xte)[:, 1]
        y_pred = pipe.predict(Xte)

        aucs.append(roc_auc_score(yte, y_prob))
        accs.append(accuracy_score(yte, y_pred))
        rep = classification_report(yte, y_pred, output_dict=True, zero_division=0)
        rec0s.append(rep["0"]["recall"])
        prec0s.append(rep["0"]["precision"])
        logger.info("Fold %d: AUC=%.3f recall(progresión)=%.2f", fold, aucs[-1], rec0s[-1])

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
        pipe_full = build_pipeline(cfg.model_name, cat, num,
                                   use_smote=cfg.use_smote, random_state=cfg.random_state)
        pipe_full.fit(X, y)
        imp = shap_importance(pipe_full, X, results_dir)
        summary["shap_top_features"] = imp.head(10).to_dict()

    return summary


def nested_cv_evaluate(
    df: pd.DataFrame,
    cfg,
    n_splits: int = 5,
    results_dir: str = "results",
    cat_cols=None,
    num_cols=None,
    param_grid: dict | None = None,
) -> dict:
    """Validación anidada: tuning interno (GroupKFold) + evaluación externa."""
    os.makedirs(results_dir, exist_ok=True)

    cat, num = _resolve_cols(cfg, df, cat_cols, num_cols)
    X = df[cat + num]
    y = df[cfg.response_binary_col].astype(int)
    groups = df[cfg.patient_id_col]

    grid = param_grid or _DEFAULT_GRIDS.get(cfg.model_name, {})
    gkf_outer = GroupKFold(n_splits=n_splits)
    gkf_inner = GroupKFold(n_splits=3)

    aucs, best_params = [], []

    for fold, (tr_idx, te_idx) in enumerate(gkf_outer.split(X, y, groups)):
        Xtr, Xte = X.iloc[tr_idx], X.iloc[te_idx]
        ytr, yte = y.iloc[tr_idx], y.iloc[te_idx]
        grp_tr = groups.iloc[tr_idx]

        if len(set(yte)) < 2:
            logger.warning("Fold %d sin ambas clases: se omite.", fold)
            continue

        pipe = build_pipeline(cfg.model_name, cat, num,
                              use_smote=cfg.use_smote, random_state=cfg.random_state,
                              smote_k_neighbors=2)  # k pequeño: los folds internos tienen pocas minorías
        search = GridSearchCV(
            pipe, grid, cv=gkf_inner, scoring="roc_auc",
            n_jobs=-1, error_score=np.nan,
        )
        search.fit(Xtr, ytr, groups=grp_tr)

        y_prob = search.predict_proba(Xte)[:, 1]
        aucs.append(roc_auc_score(yte, y_prob))
        best_params.append(search.best_params_)
        logger.info("Fold %d: AUC=%.3f (mejores params=%s)",
                    fold, aucs[-1], search.best_params_)

    return {
        "model": cfg.model_name,
        "metodo": "validacion_anidada",
        "n_folds_validos": len(aucs),
        "auc_mean": float(np.mean(aucs)),
        "auc_std": float(np.std(aucs)),
        "mejores_hiperparametros_por_fold": best_params,
    }


def shap_importance(pipe_fitted, X: pd.DataFrame, results_dir: str) -> pd.Series:
    """Calcula la importancia SHAP (mean |SHAP|) de un pipeline ya ajustado."""
    import shap

    prep = pipe_fitted.named_steps["prep"]
    model = pipe_fitted.named_steps["model"]
    names = prep.get_feature_names_out()

    Xt = prep.transform(X)
    if hasattr(Xt, "toarray"):
        Xt = Xt.toarray()
    sample = Xt[: min(400, Xt.shape[0])]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)

    sv = shap_values
    if isinstance(sv, list):
        sv = sv[1] if len(sv) > 1 else sv[0]
    sv = np.asarray(sv)
    if sv.ndim == 3:
        sv = sv[:, :, -1]
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
