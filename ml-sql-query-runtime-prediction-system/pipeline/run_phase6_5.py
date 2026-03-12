"""Phase 6.5: Expand Features to Match Runtime Logs

Aligns the 100-row features dataset with the 4000-row runtime logs.
This ensures we have one feature row per runtime measurement for ML training.
"""

from pathlib import Path
import sys
import json

# Add parent to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.expand_features import expand_features_to_runtime_logs, save_expanded_features, validate_expansion


def main():
    """Run Phase 6.5: Expand features to match runtime logs (4000 rows)."""
    print("Phase 6.5: Expand Features to Match Runtime Logs")
    print("=" * 60)
    
    try:
        print("\nExpanding 100-row features to 4000-row runtime dataset...")
        expanded_df = expand_features_to_runtime_logs()
        
        print(f"✓ Expanded from 100 to {len(expanded_df)} rows")
        print(f"✓ Columns: {list(expanded_df.columns)}")
        
        print("\nValidating expansion...")
        validation = validate_expansion(expanded_df)
        print(f"  - Expected rows: {validation['expected_rows']}")
        print(f"  - Actual rows: {validation['actual_rows']}")
        print(f"  - Rows match: {validation['rows_match']}")
        print(f"  - No nulls: {validation['no_nulls']}")
        
        if not (validation['rows_match'] and validation['no_nulls']):
            raise ValueError("Validation failed!")
        
        print("\nSaving expanded features...")
        output_path = save_expanded_features(expanded_df)
        print(f"✓ Saved to {output_path}")
        
        print("\nExpanded dataset statistics:")
        print(f"  Shape: {expanded_df.shape}")
        print(f"  Unique queries: {expanded_df['query_id'].nunique()}")
        print(f"  Runs per query: {len(expanded_df) // expanded_df['query_id'].nunique()}")
        
        print("\nFeature columns in expanded set:")
        feature_cols = [col for col in expanded_df.columns if col not in 
                       ['query_id', 'run_number', 'execution_time', 'query_category', 'tables_used']]
        print(f"  {feature_cols}")
        
        print("\n" + "=" * 60)
        print("Phase 6.5 completed successfully!")
        print("\nNext step: Use features_expanded_4000.csv for ML training")
        return 0
    
    except Exception as e:
        print(f"\n✗ Error during Phase 6.5: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
