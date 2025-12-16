import pytest
import pandas as pd
import numpy as np
from src.core.profiling import DataProfiler

@pytest.fixture
def sample_profiling_data():
    data = {
        'price': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
        'city': ['NY', 'LA', 'SF', 'NY', 'LA', 'SF', 'NY', 'LA', 'SF', 'Chicago']
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_schema():
    return {
        'numeric': ['price', 'age'],
        'categorical': ['gender', 'city'],
        'id_like': []
    }

# Test 1: Numerical Profiling Accuracy
def test_profile_numerical_features_accuracy(sample_profiling_data, sample_schema):
    profile = DataProfiler.profile_numerical_features(
        sample_profiling_data, 
        sample_schema['numeric']
    )
    
    # Check for Price mean (should be 55.00)
    assert profile['price']['mean'] == 55.00
    # Check if Skewness is present (should be near 0 for evenly distributed 'age')
    assert 'skewness' in profile['age']

# Test 2: Categorical Profiling Accuracy
def test_profile_categorical_features_accuracy(sample_profiling_data, sample_schema):
    profile = DataProfiler.profile_categorical_features(
        sample_profiling_data, 
        sample_schema['categorical']
    )
    
    # Check Gender profile (should be 5 M, 5 F)
    assert profile['gender']['unique_count'] == 2
    assert profile['gender']['top_counts'] == [5, 5]
    assert profile['gender']['top_frequencies_pct'] == [50.0, 50.0]

    # Check City profile (NY should be 3/10 = 30%)
    assert profile['city']['top_frequencies_pct'][0] == 30.0

# Test 3: Handling Empty Column Lists
def test_profile_empty_lists(sample_profiling_data):
    assert DataProfiler.profile_numerical_features(sample_profiling_data, []) == {}
    assert DataProfiler.profile_categorical_features(sample_profiling_data, []) == {}