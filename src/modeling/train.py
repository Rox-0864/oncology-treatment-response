"""Entrenamiento y evaluación de modelos predictivos.

La pieza central es un ``Pipeline`` de scikit-learn que hace TODO el
preprocesamiento (imputación, one-hot encoding, escalado) + balanceo (SMOTE) +
el clasificador, y que se guarda ENTERO con ``joblib``.

Esto corrige un bug del proyecto original: la app entrenaba con datos ya
codificados (label encoding) pero predecía con ``pd.get_dummies`` (one-hot),
produciendo un desajuste de features. Al guardar el pipeline completo, la
codificación usada en entrenamiento y en predicción es SIEMPRE la misma.

Métrica principal: AUC-ROC (la clase minoritaria "progresión" es ~3% del total,
así que la exactitud es engañosa).
"""

from __future__ import annotations

import json
import logging
import os

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from src.utils import plotting

logger = logging.getLogger(__name__)

MODEL_FACTORIES = {
    "random_forest": lambda: RandomForestClassifier(random_state=42),
    "gradient_boosting": lambda: GradientBoostingClassifier(random_state=42),
    "logistic": lambda: LogisticRegression(max_iter=1000, random_state=42),
    "decision_tree": lambda: DecisionTreeClassifier(random_state=42),
    "xgboost": lambda: XGBClassifier(eval_metric="logloss", random_state=42),
}


def build_pipeline(
    model_name: str,
    categorical_cols,
    numeric_cols,
    use_smote: bool = True,
    random_state: int = 42,
    smote_k_neighbors: int = 5,
):
    """Construye el pipeline completo de preprocesamiento + modelo."""
    if model_name not in MODEL_FACTORIES:
        raise ValueError(f"Modelo desconocido '{model_name}'. Disponibles: {list(MODEL_FACTORIES)}")

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric_cols,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ]
    )

    if use_smote:
        return ImbPipeline(
            [
                ("prep", preprocessor),
                ("smote", SMOTE(random_state=random_state, k_neighbors=smote_k_neighbors)),
                ("model", MODEL_FACTORIES[model_name]()),
            ]
        )

    return Pipeline(
        [
            ("prep", preprocessor),
            ("model", MODEL_FACTORIES[model_name]()),
        ]
    )


def feature_importance(pipe, top_n: int = 15) -> pd.DataFrame:
    """Importancia de features para modelos basados en árboles."""
    model = pipe.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame()
    names = pipe.named_steps["prep"].get_feature_names_out()
    imp = pd.Series(model.feature_importances_, index=names)
    return imp.sort_values(ascending=False).head(top_n)


def train_and_evaluate(df: pd.DataFrame, cfg) -> dict:
    """Entrena, evalúa y guarda el pipeline + métricas + gráficos."""
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.model_dir, exist_ok=True)

    target = cfg.response_binary_col
    df = df.dropna(subset=[target]).copy()
    df[target] = df[target].astype(int)

    features = list(cfg.categorical_cols) + list(cfg.numeric_cols)
    features = [c for c in features if c in df.columns]

    X = df[features]
    y = df[target]

    logger.info("Distribución de clases: %s", dict(y.value_counts()))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg.test_size, random_state=cfg.random_state, stratify=y
    )

    pipe = build_pipeline(
        cfg.model_name,
        categorical_cols=[c for c in cfg.categorical_cols if c in df.columns],
        numeric_cols=[c for c in cfg.numeric_cols if c in df.columns],
        use_smote=cfg.use_smote,
        random_state=cfg.random_state,
    )
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    metrics = {
        "model": cfg.model_name,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "class_distribution": {str(k): int(v) for k, v in y.value_counts().items()},
    }

    # Guardar artefactos
    model_path = os.path.join(cfg.model_dir, f"{cfg.model_name}_pipeline.pkl")
    joblib.dump(pipe, model_path)

    with open(os.path.join(cfg.results_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    with open(os.path.join(cfg.results_dir, "classification_report.txt"), "w") as f:
        f.write(classification_report(y_test, y_pred))

    plotting.save_confusion_matrix(cm, ["Fracaso", "Éxito"], cfg.results_dir)
    plotting.save_roc_curve(y_test, y_prob, cfg.results_dir)

    imp = feature_importance(pipe)
    if not imp.empty:
        imp.to_csv(os.path.join(cfg.results_dir, "feature_importance.csv"))
        logger.info("Importancia de features:\n%s", imp.to_string())

    logger.info("Métricas: %s", metrics)
    return {"metrics": metrics, "model_path": model_path, "report": report}
