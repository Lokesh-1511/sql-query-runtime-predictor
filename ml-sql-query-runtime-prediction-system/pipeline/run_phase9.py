"""Phase 9: ML Model Training and Evaluation

Complete training pipeline for SQL runtime prediction.
Implements recommended preprocessing, multiple model training, evaluation,
and persistence of the best model for downstream explainability.
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
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).parent.parent))

ARTIFACTS_DIR = Path("models")
BEST_MODEL_PATH = ARTIFACTS_DIR / "best_runtime_model.joblib"
TRAINING_METADATA_PATH = ARTIFACTS_DIR / "training_metadata.json"
MODEL_RESULTS_PATH = Path("data") / "phase9_model_results.csv"
PREDICTIONS_PATH = Path("data") / "phase9_best_model_predictions.csv"


def load_and_prepare_data(
    csv_path: str = 'data/ml_training_dataset.csv',
    verbose: bool = True,
) -> tuple:
    """
    Load dataset and perform preprocessing.
    
    Returns:
        X_train, X_test, y_train, y_test, X, y, df
    """
    if verbose:
        print("=" * 70)
        print("PHASE 9: ML MODEL TRAINING AND EVALUATION")
        print("=" * 70)
    
    # Step 1: Load
    if verbose:
        print("\n[Step 1] Loading dataset...")
    df = pd.read_csv(csv_path)
    if verbose:
        print(f"  ✓ Loaded {df.shape[0]} samples × {df.shape[1]} columns")
    
    # Step 2: Drop non-predictive columns
    if verbose:
        print("\n[Step 2] Dropping non-predictive columns...")
    df = df.drop(columns=["query_id", "run_number", "tables_used"])
    if verbose:
        print(f"  ✓ Dropped: query_id, run_number, tables_used")
    
    # Step 3: Encode categorical
    if verbose:
        print("\n[Step 3] Encoding categorical features...")
    df = pd.get_dummies(df, columns=["query_category"])
    if verbose:
        print(f"  ✓ One-hot encoded query_category")
        print(f"  ✓ New shape: {df.shape}")
    
    # Step 4: Log transform target
    if verbose:
        print("\n[Step 4] Creating target variable with log transform...")
    df["log_runtime"] = np.log1p(df["execution_time"])
    y = df["log_runtime"]
    X = df.drop(columns=["execution_time", "log_runtime"])
    if verbose:
        print(f"  ✓ Original runtime: min={df['execution_time'].min():.6f}s, max={df['execution_time'].max():.6f}s")
        print(f"  ✓ Log runtime: min={y.min():.4f}, max={y.max():.4f}")
        print(f"  ✓ Features: {X.shape[1]}")
        print(f"  ✓ Feature list: {list(X.columns)}")
    
    # Step 5: Train/test split
    if verbose:
        print("\n[Step 5] Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    if verbose:
        print(f"  ✓ Train: {X_train.shape[0]} samples")
        print(f"  ✓ Test:  {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test, X, y, df


def train_models(X_train, X_test, y_train, y_test) -> dict:
    """
    Train multiple models and evaluate.
    
    Returns:
        Dictionary of model names -> (model, metrics)
    """
    print("\n" + "=" * 70)
    print("TRAINING MODELS")
    print("=" * 70)
    
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    }
    
    # Try to import XGBoost
    try:
        import xgboost as xgb
        models["XGBoost"] = xgb.XGBRegressor(n_estimators=100, random_state=42)
    except ImportError:
        print("⚠ XGBoost not installed - skipping. Install with: pip install xgboost")
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'model': model,
            'y_pred': y_pred,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
        }
        
        print(f"  MAE:  {mae:.6f} (log scale)")
        print(f"  RMSE: {rmse:.6f} (log scale)")
        print(f"  R²:   {r2:.4f}")
    
    return results


def evaluate_and_rank(results: dict):
    """Display ranked model performance."""
    print("\n" + "=" * 70)
    print("MODEL RANKINGS")
    print("=" * 70)
    
    # Sort by R² score
    ranked = sorted(results.items(), key=lambda x: x[1]['r2'], reverse=True)
    
    print(f"\n{'Rank':<6} {'Model':<25} {'R²':<10} {'MAE':<10} {'RMSE':<10}")
    print("-" * 70)
    
    for rank, (name, metrics) in enumerate(ranked, 1):
        print(f"{rank:<6} {name:<25} {metrics['r2']:<10.4f} {metrics['mae']:<10.6f} {metrics['rmse']:<10.6f}")
    
    best_name, best_metrics = ranked[0]
    print("\n" + "=" * 70)
    print(f"BEST MODEL: {best_name}")
    print(f"  R² Score:   {best_metrics['r2']:.4f}")
    print(f"  MAE:        {best_metrics['mae']:.6f}")
    print(f"  RMSE:       {best_metrics['rmse']:.6f}")
    print("=" * 70)
    
    return best_name, best_metrics


def save_training_artifacts(
    best_name: str,
    best_metrics: dict,
    results: dict,
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
        },
    }
    TRAINING_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    model_results_df = pd.DataFrame(
        [
            {
                "model": name,
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "r2": metrics["r2"],
            }
            for name, metrics in results.items()
        ]
    ).sort_values("r2", ascending=False)
    model_results_df.to_csv(MODEL_RESULTS_PATH, index=False)

    predictions_df = pd.DataFrame(
        {
            "actual_log_runtime": y_test.to_numpy(),
            "predicted_log_runtime": best_metrics["y_pred"],
            "actual_runtime": np.expm1(y_test.to_numpy()),
            "predicted_runtime": np.expm1(best_metrics["y_pred"]),
        },
        index=X_test.index,
    )
    predictions_df.index.name = "row_id"
    predictions_df.to_csv(PREDICTIONS_PATH)

    print(f"  ✓ Saved: {BEST_MODEL_PATH}")
    print(f"  ✓ Saved: {TRAINING_METADATA_PATH}")
    print(f"  ✓ Saved: {MODEL_RESULTS_PATH}")
    print(f"  ✓ Saved: {PREDICTIONS_PATH}")


def plot_results(best_name: str, best_metrics: dict, y_test, X_test):
    """Create visualization of model performance."""
    print("\n[Plotting] Generating visualizations...")
    
    y_pred = best_metrics['y_pred']
    model = best_metrics['model']
    
    # Predictions vs Actual
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_pred, alpha=0.5, s=30)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
    plt.xlabel('Actual (log scale)')
    plt.ylabel('Predicted (log scale)')
    plt.title(f'{best_name} - Predictions vs Actual')
    plt.grid(True, alpha=0.3)
    
    # Residuals
    residuals = y_test - y_pred
    plt.subplot(1, 2, 2)
    plt.scatter(y_pred, residuals, alpha=0.5, s=30)
    plt.axhline(y=0, color='r', linestyle='--', lw=2)
    plt.xlabel('Predicted')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('model_evaluation.png', dpi=300)
    print(f"  ✓ Saved: model_evaluation.png")
    plt.close()
    
    # Feature Importance (for tree-based models)
    if hasattr(model, 'feature_importances_'):
        plt.figure(figsize=(10, 6))
        feature_importance = pd.DataFrame({
            'feature': X_test.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=True).tail(15)
        
        plt.barh(feature_importance['feature'], feature_importance['importance'])
        plt.xlabel('Importance')
        plt.title(f'{best_name} - Top 15 Feature Importance')
        plt.tight_layout()
        plt.savefig('feature_importance.png', dpi=300)
        print(f"  ✓ Saved: feature_importance.png")
        plt.close()
        
        # Print feature importance
        print(f"\n[Feature Importance] Top 10 features:")
        top_features = feature_importance.sort_values('importance', ascending=False).head(10)
        for _, row in top_features.iterrows():
            print(f"  {row['feature']:30s}: {row['importance']:.4f}")


def main():
    """Main training pipeline."""
    try:
        # Load and prepare
        X_train, X_test, y_train, y_test, X, y, df = load_and_prepare_data()
        
        # Train models
        results = train_models(X_train, X_test, y_train, y_test)
        
        # Evaluate and rank
        best_name, best_metrics = evaluate_and_rank(results)

        # Persist model and evaluation outputs for explainability
        save_training_artifacts(best_name, best_metrics, results, X_test, y_test)
        
        # Visualize
        plot_results(best_name, best_metrics, y_test, X_test)
        
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
    exit(main())
