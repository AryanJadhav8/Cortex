import pytest
import pandas as pd
import numpy as np
from src.core.imbalance import ImbalanceAnalyzer

# --- Classification Fixtures ---

@pytest.fixture
def balanced_data():
    return pd.DataFrame({'target': ['A'] * 50 + ['B'] * 50}) # Ratio 1.0 (LOW)

@pytest.fixture
def medium_imbalance_data():
    return pd.DataFrame({'target': ['Yes'] * 80 + ['No'] * 20}) # Ratio 20/80 = 0.25 (MEDIUM)

@pytest.fixture
def severe_imbalance_data():
    return pd.DataFrame({'target': [0] * 95 + [1] * 5}) # Ratio 5/95 ≈ 0.0526 (SEVERE)

# --- Regression Fixtures ---

@pytest.fixture
def skewed_regression_data():
    # Highly skewed data (Log-normal distributions typically have high skew > 1.0)
    data = np.random.lognormal(mean=2, sigma=1.0, size=200)
    return pd.DataFrame({'target_reg': data})

# --- Classification Tests ---

def test_1_balanced_classification(balanced_data):
    result = ImbalanceAnalyzer.analyze_classification_target(balanced_data, 'target')
    assert result['severity'] == "LOW"
    assert result['imbalance_ratio'] == 1.0

def test_2_medium_imbalance(medium_imbalance_data):
    result = ImbalanceAnalyzer.analyze_classification_target(medium_imbalance_data, 'target')
    assert result['severity'] == "MEDIUM"
    assert result['imbalance_ratio'] == 0.25

def test_3_severe_imbalance(severe_imbalance_data):
    result = ImbalanceAnalyzer.analyze_classification_target(severe_imbalance_data, 'target')
    assert result['severity'] == "SEVERE"
    assert result['imbalance_ratio'] < 0.10
    assert result['minority_class'] == 1
    assert "will likely suffer" in result['warning']

# --- Regression Tests ---

def test_4_skewed_regression(skewed_regression_data):
    result = ImbalanceAnalyzer.analyze_regression_target(skewed_regression_data, 'target_reg')
    
    # Skewness should be high (check against our 1.0 threshold)
    assert result['skewness'] > 1.0 
    assert result['skew_severity'] == "HIGH"
    assert "log/root transformation" in result['warning']

def test_5_regression_outlier_detection(skewed_regression_data):
    result = ImbalanceAnalyzer.analyze_regression_target(skewed_regression_data, 'target_reg')
    # Log-normal data naturally produces outliers detected by the IQR method
    assert result['outlier_count'] > 0 

# --- Edge Cases ---

def test_6_single_class_target():
    df = pd.DataFrame({'target': [1] * 10})
    result = ImbalanceAnalyzer.analyze_classification_target(df, 'target')
    assert result['status'] == "Single Class Detected."
    
def test_7_empty_regression_target():
    df = pd.DataFrame({'target_reg': [np.nan] * 10})
    result = ImbalanceAnalyzer.analyze_regression_target(df, 'target_reg')
    assert result['status'] == "Target column is empty."