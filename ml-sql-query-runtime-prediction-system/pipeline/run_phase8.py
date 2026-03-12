"""Phase 8: Build Final ML Training Dataset

Combines structural features, plan metrics, and runtime metadata
into a single 4000-row dataset ready for model training.
"""

from pathlib import Path
import sys

# Add parent to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.build_training_dataset import build_training_dataset, save_training_dataset, validate_training_dataset


def main():
    """Run Phase 8: Build final ML training dataset."""
    print("Phase 8: Build Final ML Training Dataset")
    print("=" * 70)
    
    try:
        print("\nCombining features, plan metrics, and runtime metadata...")
        training_df = build_training_dataset()
        
        print(f"✓ Built training dataset with shape: {training_df.shape}")
        print(f"✓ Columns ({len(training_df.columns)}): {list(training_df.columns)}")
        
        print("\nValidating training dataset...")
        validation = validate_training_dataset(training_df)
        print(f"  - Shape: {validation['shape']}")
        print(f"  - Expected rows: {validation['expected_rows']} | Actual: {len(training_df)}")
        print(f"  - Rows match: {validation['rows_match']}")
        print(f"  - Unique queries: {validation['unique_queries']}")
        print(f"  - Runs per query: {validation['runs_per_query']}")
        
        # Check nulls
        nulls = validation['null_counts']
        non_zero_nulls = {k: v for k, v in nulls.items() if v > 0}
        if non_zero_nulls:
            print(f"  - Columns with nulls: {non_zero_nulls}")
        else:
            print(f"  - Null count: 0 (all columns populated)")
        
        # Target variable statistics
        print("\nTarget variable (execution_time) statistics:")
        print(f"  - Min: {training_df['execution_time'].min():.6f} seconds")
        print(f"  - Max: {training_df['execution_time'].max():.6f} seconds")
        print(f"  - Mean: {training_df['execution_time'].mean():.6f} seconds")
        print(f"  - Std: {training_df['execution_time'].std():.6f} seconds")
        print(f"  - Median: {training_df['execution_time'].median():.6f} seconds")
        
        # Feature types breakdown
        numeric_cols = training_df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = training_df.select_dtypes(include=['object']).columns
        print(f"\nFeature composition:")
        print(f"  - Numeric features: {len(numeric_cols)}")
        print(f"  - Categorical features: {len(categorical_cols)}")
        print(f"  - Target variable: execution_time")
        
        print("\nSaving training dataset...")
        output_path = save_training_dataset(training_df)
        print(f"✓ Saved to {output_path}")
        
        print("\n" + "=" * 70)
        print("Phase 8 completed successfully!")
        print(f"\nDataset ready for ML training:")
        print(f"  - Rows (samples): {len(training_df)}")
        print(f"  - Features: {len(training_df.columns) - 3}")  # -3 for query_id, run_number, execution_time
        print(f"  - Target: execution_time (continuous, regression task)")
        return 0
    
    except Exception as e:
        print(f"\n✗ Error during Phase 8: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
