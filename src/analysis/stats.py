"""Pruebas estadísticas para el análisis de asociaciones.

Cada función devuelve un dict con el estadístico y el valor p, de modo que los
resultados puedan registrarse y revisarse de forma consistente (en lugar de
quedar dispersos en celdas de notebook).
"""

from __future__ import annotations

import pandas as pd
from scipy import stats
from scipy.stats import fisher_exact
from statsmodels.formula.api import ols
from statsmodels.stats.proportion import proportions_ztest


def chi2_test(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """Test chi-cuadrado de independencia entre dos variables categóricas."""
    table = pd.crosstab(df[col1], df[col2])
    chi2, p, dof, expected = stats.chi2_contingency(table)
    return {"chi2": float(chi2), "p_value": float(p), "dof": int(dof), "table": table}


def anova_test(df: pd.DataFrame, numeric_col: str, group_col: str) -> dict:
    """ANOVA de una vía: media de ``numeric_col`` entre grupos de ``group_col``."""
    model = ols(f'Q("{numeric_col}") ~ C(Q("{group_col}"))', data=df).fit()
    return {
        "f_value": float(model.fvalue),
        "p_value": float(model.f_pvalue),
        "r_squared": float(model.rsquared),
    }


def fisher_test(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """Test exacto de Fisher (para tablas 2x2)."""
    table = pd.crosstab(df[col1], df[col2])
    oddsratio, p = fisher_exact(table)
    return {"odds_ratio": float(oddsratio), "p_value": float(p)}


def ztest_proportions(success_a: int, n_a: int, success_b: int, n_b: int) -> dict:
    """Test Z de proporciones entre dos grupos (A/B testing)."""
    z, p = proportions_ztest([success_a, success_b], [n_a, n_b])
    return {"z": float(z), "p_value": float(p)}
