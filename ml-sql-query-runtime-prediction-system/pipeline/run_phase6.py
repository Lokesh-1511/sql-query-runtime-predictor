"""Phase 6: Structural Feature Extraction

Extracts SQL structural features from the execution dataset and combines them
with runtime metrics to create a comprehensive features dataset for ML modeling.
"""

from pathlib import Path
import sys

# Add parent to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.feature_extractor import process_execution_dataset, save_features_dataset


def main():
    """Run Phase 6: Extract structural features from execution dataset."""
    print("Phase 6: Structural Feature Extraction")
    print("=" * 50)
    
    try:
        print("\nProcessing execution dataset...")
        features_df = process_execution_dataset()
        
        print(f"✓ Generated {len(features_df)} feature rows")
        print(f"✓ Columns: {list(features_df.columns)}")
        
        print("\nFeature statistics:")
        print(features_df.describe())
        
        print("\nSaving features dataset...")
        output_path = save_features_dataset(features_df)
        print(f"✓ Saved to {output_path}")
        
        print("\n" + "=" * 50)
        print("Phase 6 completed successfully!")
        return 0
    
    except Exception as e:
        print(f"\n✗ Error during Phase 6: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
