import pandas as pd
import numpy as np
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modeling.baseline import BaselineModeler

def test_shap_run():
    print("🚀 Starting SHAP Integration Test...")
    
    # 1. Create BIGGER dummy data (Need more rows for 5-fold CV)
    data = pd.DataFrame({
        'age': [22, 38, 26, 35, 35, 23, 45, 18, 30, 40, 50, 20, 25, 33, 42],
        'fare': [7.25, 71.28, 7.92, 53.10, 8.05, 8.45, 10.50, 7.00, 15.00, 20.00, 100.0, 8.0, 9.0, 12.0, 15.0],
        'sex': ['male', 'female', 'female', 'female', 'male', 'female', 'male', 'male', 'female', 'male', 'female', 'male', 'female', 'male', 'female'],
        'survived': [0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1] # Balanced enough for CV
    })
    schema = {'numeric': ['age', 'fare'], 'categorical': ['sex']}
    
    try:
        print("Model is training and calculating SHAP values...")
        # Note: target_is_numeric is False here because survived is 0/1 (Classification)
        result = BaselineModeler.run_baseline_model(data, 'survived', schema, is_classification=True)
        
        if "error" in result:
            print(f"❌ Test Failed with Error: {result['error']}")
            return

        # 3. Verify SHAP data exists
        if "shap_data" in result:
            print("✅ Success: 'shap_data' found in result dictionary.")
            print(f"✅ Base Value: {round(result['shap_data']['base_value'], 4)}")
            print(f"✅ Number of SHAP records: {len(result['shap_data']['values'])}")
            print("🎉 SHAP Integration is working flawlessly!")
        else:
            print("❌ Test Failed: 'shap_data' key not found in output.")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_shap_run()