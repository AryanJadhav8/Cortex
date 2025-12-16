import pytest
import pandas as pd
import numpy as np
from src.core.health import DataHealth

# Setup a test DataFrame with specific characteristics
@pytest.fixture
def sample_dataframe():
    data = {
        'ID': range(100),  # High cardinality (99 unique if one row is duplicated)
        'Feature_A': [10] * 50 + [np.nan] * 50, # 50% missing
        'Feature_B': ['X', 'Y', 'Z'] * 33 + ['X'], # Low cardinality (3 unique)
        'Feature_C': [1.0, 2.0] * 50,
        'Constant_Col': [5] * 100
    }
    df = pd.DataFrame(data)
    # Manually create one full duplicate row at index 99
    df.loc[99] = df.loc[98] 
    return df

# Test 1: Missing Data Summary Accuracy
def test_missing_data_summary(sample_dataframe):
    missing_df = DataHealth.get_missing_data_summary(sample_dataframe)
    
    # Only Feature_A should be present in the summary
    assert 'Feature_A' in missing_df.index
    assert 'Feature_B' not in missing_df.index
    
    # Check if count and percent are correct (50 rows missing in 100 rows)
    assert missing_df.loc['Feature_A', 'Missing Count'] == 50
    assert missing_df.loc['Feature_A', 'Missing Percent'] == 50.0

# Test 2: Duplicate Row Summary Accuracy
def test_duplicate_summary(sample_dataframe):
    summary = DataHealth.get_duplicate_summary(sample_dataframe)
    
    # Total rows is 100, one duplicate created at index 99
    assert summary['total_rows'] == 100
    assert summary['duplicate_rows'] == 1
    assert summary['duplicate_percent'] == 1.0

# Test 3: Column Cardinality Flagging
def test_column_cardinality(sample_dataframe):
    cardinality_df = DataHealth.get_column_cardinality(sample_dataframe)
    
    # ID should be flagged as High Cardinality (99 unique in 100 rows, >90%)
    assert cardinality_df.loc['ID', 'Unique Values'] == 99
    assert cardinality_df.loc['ID', 'Cardinality Flag'] == 'High (Potential ID)'
    
    # Feature_B should be Low/Medium Cardinality (3 unique)
    assert cardinality_df.loc['Feature_B', 'Unique Values'] == 3
    assert cardinality_df.loc['Feature_B', 'Cardinality Flag'] == 'Low/Medium'

# Test 4: Constant Column Check (Implicitly tested by cardinality)
def test_constant_column(sample_dataframe):
    cardinality_df = DataHealth.get_column_cardinality(sample_dataframe)
    
    # Constant_Col should have 1 unique value
    assert cardinality_df.loc['Constant_Col', 'Unique Values'] == 1
    assert cardinality_df.loc['Constant_Col', 'Cardinality Flag'] == 'Low/Medium'