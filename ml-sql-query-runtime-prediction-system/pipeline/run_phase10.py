"""Phase 10: Model Explainability and Feature Attribution.

Loads the persisted best model from Phase 9 and generates SHAP-based
explanations plus feature attribution artifacts.
"""

from __future__ import annotations

from pathlib import Path
import json
import sys

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import shap

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.run_phase9 import load_and_prepare_data

MODELS_DIR = Path("models")
BEST_MODEL_PATH = MODELS_DIR / "best_runtime_model.joblib"
TRAINING_METADATA_PATH = MODELS_DIR / "training_metadata.json"
SHAP_VALUES_PATH = Path("data") / "phase10_shap_values.csv"
SHAP_IMPORTANCE_PATH = Path("data") / "phase10_shap_feature_importance.csv"
SHAP_SUMMARY_PNG = Path("shap_summary.png")
SHAP_BAR_PNG = Path("shap_importance_bar.png")


def load_phase9_artifacts() -> tuple[object, dict]:
    """Load persisted best model and metadata from Phase 9."""
    if not BEST_MODEL_PATH.exists() or not TRAINING_METADATA_PATH.exists():
        raise FileNotFoundError(
            "Phase 9 artifacts are missing. Run pipeline/run_phase9.py first."
        )

    model = joblib.load(BEST_MODEL_PATH)
    metadata = json.loads(TRAINING_METADATA_PATH.read_text(encoding="utf-8"))
    return model, metadata


def compute_shap_outputs(model: object, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute per-row SHAP values and global mean absolute importance."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    if hasattr(shap_values, "values"):
        shap_array = shap_values.values
    else:
        shap_array = shap_values

    shap_values_df = pd.DataFrame(shap_array, columns=X_test.columns, index=X_test.index)
    shap_values_df.index.name = "row_id"

    importance_df = pd.DataFrame(
        {
            "feature": X_test.columns,
            "mean_abs_shap": shap_values_df.abs().mean(axis=0).to_numpy(),
        }
    ).sort_values("mean_abs_shap", ascending=False)

    return shap_values_df, importance_df


def save_shap_plots(model: object, X_test: pd.DataFrame) -> None:
    """Generate SHAP summary and bar plots."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    plt.savefig(SHAP_SUMMARY_PNG, dpi=300, bbox_inches="tight")
    plt.close()

    shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(SHAP_BAR_PNG, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> int:
    """Run Phase 10 explainability analysis."""
    try:
        print("=" * 70)
        print("PHASE 10: MODEL EXPLAINABILITY AND FEATURE ATTRIBUTION")
        print("=" * 70)

        print("\n[Step 1] Loading Phase 9 artifacts...")
        model, metadata = load_phase9_artifacts()
        print(f"  ✓ Loaded best model: {metadata['best_model_name']}")
        print(f"  ✓ Loaded feature schema with {len(metadata['feature_names'])} features")

        print("\n[Step 2] Recreating deterministic test split...")
        _, X_test, _, y_test, _, _, _ = load_and_prepare_data(verbose=False)
        print(f"  ✓ Test rows available for explainability: {len(X_test)}")

        print("\n[Step 3] Computing SHAP values...")
        shap_values_df, importance_df = compute_shap_outputs(model, X_test)
        SHAP_VALUES_PATH.parent.mkdir(parents=True, exist_ok=True)
        shap_values_df.to_csv(SHAP_VALUES_PATH)
        importance_df.to_csv(SHAP_IMPORTANCE_PATH, index=False)
        print(f"  ✓ Saved: {SHAP_VALUES_PATH}")
        print(f"  ✓ Saved: {SHAP_IMPORTANCE_PATH}")

        print("\n[Step 4] Generating explainability plots...")
        save_shap_plots(model, X_test)
        print(f"  ✓ Saved: {SHAP_SUMMARY_PNG}")
        print(f"  ✓ Saved: {SHAP_BAR_PNG}")

        print("\n[Step 5] Top SHAP features...")
        top_features = importance_df.head(10)
        for _, row in top_features.iterrows():
            print(f"  {row['feature']:30s}: {row['mean_abs_shap']:.6f}")

        print("\n[Step 6] Model performance reference... ")
        print(f"  ✓ Best model: {metadata['best_model_name']}")
        print(f"  ✓ R²:   {metadata['metrics']['r2']:.4f}")
        print(f"  ✓ MAE:  {metadata['metrics']['mae']:.6f} (log scale)")
        print(f"  ✓ RMSE: {metadata['metrics']['rmse']:.6f} (log scale)")
        print(f"  ✓ Test samples explained: {len(y_test)}")

        print("\n" + "=" * 70)
        print("✅ PHASE 10 COMPLETE")
        print("=" * 70)
        print("\nNext Phase: Phase 11 - Model serving / deployment API")
        return 0
    except Exception as exc:
        print(f"\n❌ Error: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())