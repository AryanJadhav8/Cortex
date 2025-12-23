import sys
import os

# 1. Immediate Print (Before anything else)
print("1. Python script started...", flush=True)

try:
    import pandas as pd
    import numpy as np
    print("2. Libraries imported successfully...", flush=True)
except Exception as e:
    print(f"FAILED at library import: {e}", flush=True)
    sys.exit(1)

# Ensure 'src' is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.core.remediator import DataRemediator
    print("3. DataRemediator imported successfully...", flush=True)
except Exception as e:
    print(f"FAILED at importing Remediator: {e}", flush=True)
    sys.exit(1)

def run_remediation_test():
    print("4. Starting test logic...", flush=True)
    
    # Create data with enough rows to satisfy KNN (k=2)
    data = pd.DataFrame({
        'age': [20, np.nan, 30, 40, 50],
        'fare': [10, 11, 10, 50, 45],
        'survived': [0, 1, 0, 1, 0]
    })
    
    print(f"5. Data created. Missing values: {data['age'].isnull().sum()}", flush=True)
    
    try:
        remediator = DataRemediator()
        print("6. Calling smart_impute...", flush=True)
        healed_df = remediator.smart_impute(data, 'survived')
        
        missing_after = healed_df['age'].isnull().sum()
        print(f"7. Missing values after: {missing_after}", flush=True)
        
        if missing_after == 0:
            print("✅ SUCCESS: Data is healed!", flush=True)
            print(healed_df)
        else:
            print("❌ FAILURE: Still has missing values.", flush=True)

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}", flush=True)

if __name__ == "__main__":
    run_remediation_test()