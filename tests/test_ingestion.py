import pytest
import pandas as pd
import io
from src.core.ingestion import DataLoader

# 1. Test Valid Data
def test_load_valid_csv():
    csv_content = "name,age,score\nAlice,30,90\nBob,25,85"
    # Convert string to a file-like object
    file_buffer = io.StringIO(csv_content)
    
    df = DataLoader.load_file(file_buffer)
    
    assert df.shape == (2, 3)
    assert "name" in df.columns

# 2. Test Empty File (Should fail)
def test_load_empty_file():
    empty_buffer = io.StringIO("")
    
    with pytest.raises(ValueError, match="empty"):
        DataLoader.load_file(empty_buffer)

# 3. Test Duplicate Columns (Should fail)
def test_duplicate_columns():
    # 'age' appears twice
    csv_content = "name,age,age\nAlice,30,30"
    file_buffer = io.StringIO(csv_content)
    
    with pytest.raises(ValueError, match="Duplicate column"):
        DataLoader.load_file(file_buffer)

# 4. Test Schema Inference
def test_schema_inference():
    data = {
        'id': range(100),                # ID-like (100 unique, 100 rows)
        'price': [10.5] * 100,           # Numeric
        'category': ['A'] * 100          # Categorical
    }
    df = pd.DataFrame(data)
    
    schema = DataLoader.infer_schema(df)
    
    assert 'id' in schema['id_like']
    assert 'price' in schema['numeric']
    assert 'category' in schema['categorical']