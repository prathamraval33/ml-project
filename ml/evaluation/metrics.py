"""Evaluation metrics module for CineForecast models.

Provides standardized regression and classification metric computations
on both log-transformed and original USD scales.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from scipy.stats import pearsonr


def calculate_regression_metrics(
    y_true_log: np.ndarray,
    y_pred_log: np.ndarray,
    prefix: str = "",
) -> Dict[str, float]:
    """Calculate comprehensive regression evaluation metrics on both log and dollar scales.

    Args:
        y_true_log: Ground truth values in log1p space (ln(revenue + 1)).
        y_pred_log: Model predicted values in log1p space.
        prefix: Optional prefix for metric dictionary keys.

    Returns:
        Dictionary containing RMSE, MAE, R², Pearson R, and dollar-scale errors.
    """
    y_true_log = np.asarray(y_true_log, dtype=np.float64)
    y_pred_log = np.asarray(y_pred_log, dtype=np.float64)

    # Log-scale metrics
    rmse_log = float(np.sqrt(mean_squared_error(y_true_log, y_pred_log)))
    mae_log = float(mean_absolute_error(y_true_log, y_pred_log))
    r2_log = float(r2_score(y_true_log, y_pred_log))

    # Pearson correlation on log scale
    if len(y_true_log) > 1:
        corr_log, _ = pearsonr(y_true_log, y_pred_log)
        corr_log = float(corr_log)
    else:
        corr_log = 0.0

    # Back-transformed USD scale metrics (expm1)
    y_true_usd = np.expm1(np.clip(y_true_log, 0, 30))
    y_pred_usd = np.expm1(np.clip(y_pred_log, 0, 30))

    rmse_usd = float(np.sqrt(mean_squared_error(y_true_usd, y_pred_usd)))
    mae_usd = float(mean_absolute_error(y_true_usd, y_pred_usd))
    r2_usd = float(r2_score(y_true_usd, y_pred_usd))

    # Median Absolute Percentage Error (MdAPE) on USD scale
    nonzero_mask = y_true_usd > 0
    if np.any(nonzero_mask):
        mdape = float(
            np.median(
                np.abs(y_true_usd[nonzero_mask] - y_pred_usd[nonzero_mask])
                / y_true_usd[nonzero_mask]
            )
            * 100.0
        )
    else:
        mdape = 0.0

    p = f"{prefix}_" if prefix else ""
    return {
        f"{p}rmse_log": round(rmse_log, 4),
        f"{p}mae_log": round(mae_log, 4),
        f"{p}r2_log": round(r2_log, 4),
        f"{p}pearson_r": round(corr_log, 4),
        f"{p}rmse_usd": round(rmse_usd, 2),
        f"{p}mae_usd": round(mae_usd, 2),
        f"{p}r2_usd": round(r2_usd, 4),
        f"{p}mdape_percent": round(mdape, 2),
    }


def calculate_classification_metrics(
    y_true: Union[List[str], np.ndarray, pd.Series],
    y_pred: Union[List[str], np.ndarray, pd.Series],
    labels: Optional[List[str]] = None,
    prefix: str = "",
) -> Dict[str, Any]:
    """Calculate multi-class classification evaluation metrics.

    Args:
        y_true: Ground truth class labels (e.g. Flop, Break-even, Hit, Blockbuster).
        y_pred: Predicted class labels.
        labels: Ordered list of unique class labels.
        prefix: Optional prefix for metric dictionary keys.

    Returns:
        Dictionary containing accuracy, macro/weighted precision, recall, F1,
        and confusion matrix breakdown.
    """
    if labels is None:
        labels = ["Flop", "Break-even", "Hit", "Blockbuster"]

    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0))
    macro_prec = float(precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)

    p = f"{prefix}_" if prefix else ""
    return {
        f"{p}accuracy": round(acc, 4),
        f"{p}macro_f1": round(macro_f1, 4),
        f"{p}weighted_f1": round(weighted_f1, 4),
        f"{p}macro_precision": round(macro_prec, 4),
        f"{p}macro_recall": round(macro_rec, 4),
        f"{p}confusion_matrix": cm.tolist(),
        f"{p}labels": labels,
        f"{p}per_class_report": report,
    }
