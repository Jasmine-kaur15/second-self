"""Phase 5: Orchestration. Sequentially runs classify.py -> link.py -> build_graph.py."""

import sys
import classify
import link
import build_graph

def run_pipeline():
    print("=" * 50)
    print("STARTING SECOND-SELF PIPELINE")
    print("=" * 50)
    
    try:
        print("\n--- STEP 1: CLASSIFYING NEW NOTES ---")
        classify.main()
        
        print("\n--- STEP 2: AUTO-LINKING ---")
        link.main()
        
        print("\n--- STEP 3: BUILDING GRAPH ---")
        build_graph.main()
        
        print("\n" + "=" * 50)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 50)
        return True
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"PIPELINE FAILED: {e}")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
