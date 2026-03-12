"""Phase 9: ML Model Training and Evaluation.

Strengthened training pipeline with engineered features, 5-fold cross-validation,
XGBoost hyperparameter search, richer evaluation artifacts, and model
persistence for downstream explainability and deployment.
"""

from pathlib import Path
import json
import sys

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_val_score, train_test_split
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).parent.parent))

ARTIFACTS_DIR = Path("models")
BEST_MODEL_PATH = ARTIFACTS_DIR / "best_runtime_model.joblib"
TRAINING_METADATA_PATH = ARTIFACTS_DIR / "training_metadata.json"
MODEL_RESULTS_PATH = Path("data") / "phase9_model_results.csv"
PREDICTIONS_PATH = Path("data") / "phase9_best_model_predictions.csv"
FEATURE_IMPORTANCE_PATH = Path("data") / "phase9_feature_importance.csv"


def load_and_prepare_data(
    csv_path: str = "data/ml_training_dataset.csv",
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame]:
    """Load dataset, preprocess features, and return train/test splits plus full matrices."""
    if verbose:
        print("=" * 70)
        print("PHASE 9: ML MODEL TRAINING AND EVALUATION")
        print("=" * 70)
        print("\n[Step 1] Loading dataset...")

    df = pd.read_csv(csv_path)
    if verbose:
        print(f"  ✓ Loaded {df.shape[0]} samples × {df.shape[1]} columns")
        print("\n[Step 2] Dropping non-predictive columns...")

    df = df.drop(columns=["query_id", "run_number", "tables_used"])
    if verbose:
        print("  ✓ Dropped: query_id, run_number, tables_used")
        print("\n[Step 3] Encoding categorical features...")

    df = pd.get_dummies(df, columns=["query_category"])
    if verbose:
        print("  ✓ One-hot encoded query_category")
        print(f"  ✓ New shape: {df.shape}")
        print("\n[Step 4] Creating target variable with log transform...")

    df["log_runtime"] = np.log1p(df["execution_time"])
    y = df["log_runtime"]
    X = df.drop(columns=["execution_time", "log_runtime"])

    if verbose:
        print(f"  ✓ Original runtime: min={df['execution_time'].min():.6f}s, max={df['execution_time'].max():.6f}s")
        print(f"  ✓ Log runtime: min={y.min():.4f}, max={y.max():.4f}")
        print(f"  ✓ Features: {X.shape[1]}")
        print(f"  ✓ Feature list: {list(X.columns)}")
        print("\n[Step 5] Splitting data (80/20)...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    if verbose:
        print(f"  ✓ Train: {X_train.shape[0]} samples")
        print(f"  ✓ Test:  {X_test.shape[0]} samples")

    return X_train, X_test, y_train, y_test, X, y, df


def build_candidate_models() -> dict[str, object]:
    """Return baseline candidate regressors for CV benchmarking."""
    return {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, random_state=42),
        "XGBoost Baseline": xgb.XGBRegressor(
            objective="reg:squarederror",
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=1,
        ),
    }


def evaluate_regressor(model: object, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> dict[str, object]:
    """Fit a regressor and compute held-out metrics."""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = r2_score(y_test, y_pred)
    return {
        "model": model,
        "y_pred": y_pred,
        "mae": float(mae),
        "rmse": rmse,
        "r2": float(r2),
    }


def train_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    X: pd.DataFrame,
    y: pd.Series,
) -> dict[str, dict[str, object]]:
    """Train baseline models with 5-fold CV and tune XGBoost with RandomizedSearchCV."""
    print("\n" + "=" * 70)
    print("TRAINING MODELS")
    print("=" * 70)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    results: dict[str, dict[str, object]] = {}

    for name, model in build_candidate_models().items():
        print(f"\nTraining {name}...")
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring="r2", n_jobs=-1)
        metrics = evaluate_regressor(model, X_train, X_test, y_train, y_test)
        metrics["cv_mean_r2"] = float(cv_scores.mean())
        metrics["cv_std_r2"] = float(cv_scores.std())
        metrics["best_params"] = {}
        results[name] = metrics
        print(f"  CV R²: {metrics['cv_mean_r2']:.4f} ± {metrics['cv_std_r2']:.4f}")
        print(f"  MAE:   {metrics['mae']:.6f} (log scale)")
        print(f"  RMSE:  {metrics['rmse']:.6f} (log scale)")
        print(f"  R²:    {metrics['r2']:.4f}")

    print("\nTuning XGBoost with RandomizedSearchCV (20 iterations)...")
    search = RandomizedSearchCV(
        estimator=xgb.XGBRegressor(
            objective="reg:squarederror",
            random_state=42,
            n_jobs=1,
        ),
        param_distributions={
            "max_depth": [3, 4, 5, 6, 7, 8],
            "learning_rate": [0.01, 0.03, 0.05, 0.08, 0.1, 0.15],
            "n_estimators": [100, 150, 200, 300, 400, 500],
            "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
        },
        n_iter=20,
        scoring="r2",
        cv=cv,
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, y_train)
    tuned_metrics = evaluate_regressor(search.best_estimator_, X_train, X_test, y_train, y_test)
    tuned_metrics["cv_mean_r2"] = float(search.best_score_)
    tuned_metrics["cv_std_r2"] = 0.0
    tuned_metrics["best_params"] = search.best_params_
    results["XGBoost Tuned"] = tuned_metrics
    print(f"  Best params: {search.best_params_}")
    print(f"  CV R²: {search.best_score_:.4f}")
    print(f"  MAE:   {tuned_metrics['mae']:.6f} (log scale)")
    print(f"  RMSE:  {tuned_metrics['rmse']:.6f} (log scale)")
    print(f"  R²:    {tuned_metrics['r2']:.4f}")

    return results


def evaluate_and_rank(results: dict[str, dict[str, object]]) -> tuple[str, dict[str, object]]:
    """Display ranked model performance and return the best model entry."""
    print("\n" + "=" * 70)
    print("MODEL RANKINGS")
    print("=" * 70)

    ranked = sorted(results.items(), key=lambda item: (item[1]["r2"], item[1]["cv_mean_r2"]), reverse=True)

    print(f"\n{'Rank':<6} {'Model':<25} {'R²':<10} {'CV R²':<12} {'MAE':<10} {'RMSE':<10}")
    print("-" * 90)
    for rank, (name, metrics) in enumerate(ranked, start=1):
        print(
            f"{rank:<6} {name:<25} {metrics['r2']:<10.4f} "
            f"{metrics['cv_mean_r2']:<12.4f} {metrics['mae']:<10.6f} {metrics['rmse']:<10.6f}"
        )

    best_name, best_metrics = ranked[0]
    print("\n" + "=" * 70)
    print(f"BEST MODEL: {best_name}")
    print(f"  R² Score:        {best_metrics['r2']:.4f}")
    print(f"  Cross-val R²:    {best_metrics['cv_mean_r2']:.4f}")
    print(f"  MAE:             {best_metrics['mae']:.6f}")
    print(f"  RMSE:            {best_metrics['rmse']:.6f}")
    if best_metrics["best_params"]:
        print(f"  Best parameters: {best_metrics['best_params']}")
    print("=" * 70)
    return best_name, best_metrics


def save_training_artifacts(
    best_name: str,
    best_metrics: dict[str, object],
    results: dict[str, dict[str, object]],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> None:
    """Persist best model, metrics, and predictions for later phases."""
    print("\n[Artifacts] Saving model and evaluation outputs...")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(best_metrics["model"], BEST_MODEL_PATH)

    metadata = {
        "best_model_name": best_name,
        "target_column": "execution_time",
        "target_transform": "log1p",
        "feature_names": list(X_test.columns),
        "test_size": int(len(X_test)),
        "metrics": {
            "mae": float(best_metrics["mae"]),
            "rmse": float(best_metrics["rmse"]),
            "r2": float(best_metrics["r2"]),
            "cv_mean_r2": float(best_metrics["cv_mean_r2"]),
            "cv_std_r2": float(best_metrics["cv_std_r2"]),
        },
        "best_params": best_metrics["best_params"],
    }
    TRAINING_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    model_results_df = pd.DataFrame(
        [
            {
                "model": name,
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "r2": metrics["r2"],
                "cv_mean_r2": metrics["cv_mean_r2"],
                "cv_std_r2": metrics["cv_std_r2"],
                "best_params": json.dumps(metrics["best_params"]),
            }
            for name, metrics in results.items()
        ]
    ).sort_values(["r2", "cv_mean_r2"], ascending=False)
    model_results_df.to_csv(MODEL_RESULTS_PATH, index=False)

    predictions_df = pd.DataFrame(
        {
            "actual_log_runtime": y_test.to_numpy(),
            "predicted_log_runtime": best_metrics["y_pred"],
            "actual_runtime": np.expm1(y_test.to_numpy()),
            "predicted_runtime": np.expm1(best_metrics["y_pred"]),
            "residual_log_runtime": y_test.to_numpy() - np.asarray(best_metrics["y_pred"]),
        },
        index=X_test.index,
    )
    predictions_df.index.name = "row_id"
    predictions_df.to_csv(PREDICTIONS_PATH)

    print(f"  ✓ Saved: {BEST_MODEL_PATH}")
    print(f"  ✓ Saved: {TRAINING_METADATA_PATH}")
    print(f"  ✓ Saved: {MODEL_RESULTS_PATH}")
    print(f"  ✓ Saved: {PREDICTIONS_PATH}")


def plot_results(best_name: str, best_metrics: dict[str, object], y_test: pd.Series) -> None:
    """Generate predicted-vs-actual scatter and residual histogram."""
    print("\n[Plotting] Generating evaluation visualizations...")
    y_pred = np.asarray(best_metrics["y_pred"])
    residuals = y_test.to_numpy() - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    axes[0].scatter(y_test, y_pred, alpha=0.5, s=30)
    axes[0].plot([min_val, max_val], [min_val, max_val], "r--", lw=2)
    axes[0].set_xlabel("Actual (log scale)")
    axes[0].set_ylabel("Predicted (log scale)")
    axes[0].set_title(f"{best_name} - Predicted vs Actual")
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(residuals, bins=30, color="steelblue", edgecolor="white")
    axes[1].axvline(0, color="r", linestyle="--", lw=2)
    axes[1].set_xlabel("Residual (actual - predicted, log scale)")
    axes[1].set_ylabel("Frequency")
    axes[1].set_title("Residual Distribution")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("model_evaluation.png", dpi=300)
    plt.close(fig)
    print("  ✓ Saved: model_evaluation.png")


def analyze_feature_importance(
    best_name: str,
    best_metrics: dict[str, object],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> None:
    """Compute model and permutation importance, save combined plot and CSV."""
    print("\n[Feature Importance] Computing model and permutation importance...")
    model = best_metrics["model"]

    model_importance = getattr(model, "feature_importances_", np.zeros(X_test.shape[1], dtype=float))
    permutation = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=10,
        random_state=42,
        n_jobs=-1,
        scoring="r2",
    )

    importance_df = pd.DataFrame(
        {
            "feature": X_test.columns,
            "model_importance": model_importance,
            "permutation_importance_mean": permutation.importances_mean,
            "permutation_importance_std": permutation.importances_std,
        }
    ).sort_values("permutation_importance_mean", ascending=False)
    FEATURE_IMPORTANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)

    top_model_df = importance_df.sort_values("model_importance", ascending=False).head(15).sort_values("model_importance")
    top_permutation_df = importance_df.head(15).sort_values("permutation_importance_mean")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    axes[0].barh(top_model_df["feature"], top_model_df["model_importance"], color="darkorange")
    axes[0].set_title(f"{best_name} - feature_importances_")
    axes[0].set_xlabel("Importance")

    axes[1].barh(top_permutation_df["feature"], top_permutation_df["permutation_importance_mean"], color="seagreen")
    axes[1].set_title(f"{best_name} - Permutation Importance")
    axes[1].set_xlabel("Mean importance (R² drop)")

    fig.tight_layout()
    fig.savefig("feature_importance.png", dpi=300)
    plt.close(fig)
    print("  ✓ Saved: feature_importance.png")
    print(f"  ✓ Saved: {FEATURE_IMPORTANCE_PATH}")

    print("\n[Feature Importance] Top 10 features (permutation):")
    for _, row in importance_df.head(10).iterrows():
        print(f"  {row['feature']:30s}: {row['permutation_importance_mean']:.4f}")


def main() -> int:
    """Run the full training and evaluation pipeline."""
    try:
        X_train, X_test, y_train, y_test, X, y, _ = load_and_prepare_data()
        results = train_models(X_train, X_test, y_train, y_test, X, y)
        best_name, best_metrics = evaluate_and_rank(results)
        save_training_artifacts(best_name, best_metrics, results, X_test, y_test)
        plot_results(best_name, best_metrics, y_test)
        analyze_feature_importance(best_name, best_metrics, X_test, y_test)

        print("\n" + "=" * 70)
        print("✅ PHASE 9 COMPLETE")
        print("=" * 70)
        print("\nNext Phase: Phase 10 - Explainability Analysis (SHAP)")
        print("Or: Deploy model to API (Phase 11)")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
