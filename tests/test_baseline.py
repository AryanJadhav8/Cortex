import pytest
import pandas as pd
import numpy as np
from src.modeling.baseline import BaselineModeler

# Fixture for a standard classification problem
@pytest.fixture
def classification_data():
    df = pd.DataFrame({
        'feature_num_a': np.random.rand(50),
        'feature_num_b': np.random.rand(50) * 10,
        'feature_cat_c': ['A', 'B'] * 25,
        'target_class': [0] * 30 + [1] * 20
    })
    # Add some NaNs to ensure the pipeline handles missing data silently (though not optimally)
    df.loc[0, 'feature_num_a'] = np.nan
    df.loc[1, 'feature_cat_c'] = np.nan
    
    return df

# Fixture for data with perfect leakage (CV score will be 1.0)
@pytest.fixture
def leakage_data():
    df = pd.DataFrame({
        'feature_leak_id': range(50), # ID column, useless but not leakage
        'feature_leak_key': [f'key_{i}' for i in range(50)], # High cardinality
        'target_class': [0] * 30 + [1] * 20
    })
    # The actual leakage: A feature that perfectly maps to the target
    df['perfect_leak'] = df['target_class'].apply(lambda x: 'Y' if x == 1 else 'N')
    
    return df

@pytest.fixture
def sample_schema_class():
    return {
        'numeric': ['feature_num_a', 'feature_num_b'],
        'categorical': ['feature_cat_c'],
        'id_like': []
    }

# Test 1: Basic Classification Run
def test_1_classification_run(classification_data, sample_schema_class):
    results = BaselineModeler.run_baseline_model(
        classification_data, 'target_class', sample_schema_class, is_classification=True
    )
    
    # Check for core outputs
    assert results['model_type'] == 'Classification'
    assert 'mean_cv_score' in results
    assert len(results['cv_scores']) == 5
    assert results['mean_cv_score'] > 0.0 # Should have some predictive power
    assert results['leakage_warning'] is None # Should not trigger leakage

# Test 2: Feature Importance Extraction
def test_2_feature_importance_extraction(classification_data, sample_schema_class):
    results = BaselineModeler.run_baseline_model(
        classification_data, 'target_class', sample_schema_class, is_classification=True
    )
    importances = results['feature_importances']
    
    # Check that all features (including OHE) are present
    # Expect: feature_num_a, feature_num_b, feature_cat_c_A, feature_cat_c_B, feature_cat_c_nan
    assert len(importances) == 5
    # Check that total importance sums close to 1.0
    assert 0.99 < sum(importances.values()) <= 1.0

# Test 3: Leakage Detection Warning
def test_3_leakage_detection(leakage_data):
    schema = {
        'numeric': [],
        'categorical': ['perfect_leak', 'feature_leak_key'],
        'id_like': ['feature_leak_id']
    }
    
    # Run the model (it should achieve near perfect accuracy)
    results = BaselineModeler.run_baseline_model(
        leakage_data, 'target_class', schema, is_classification=True
    )

    assert results['model_type'] == 'Classification'
    # Score should be near 1.0 due to 'perfect_leak' feature
    assert results['mean_cv_score'] > 0.99 
    assert "SEVERE LEAKAGE DETECTED" in results['leakage_warning']
    
    # Check if the leaking feature is correctly identified as the most important
    top_feature = list(results['feature_importances'].keys())[0]
    assert 'perfect_leak' in top_feature