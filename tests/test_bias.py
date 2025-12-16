import pytest
import pandas as pd
from src.core.bias import BiasAnalyzer

# Fixture for a simulated loan dataset
@pytest.fixture
def loan_data():
    data = {
        # Group 'Male' is 80% (Privileged), 'Female' is 20% (Unprivileged) -> Representation Bias
        'Gender': ['Male'] * 800 + ['Female'] * 200,
        # 'Loan_Status': 1 is Approved (Positive Label)
        
        # Loan Status:
        # Males: 600 Approved (75% rate) / 200 Denied (25% rate)
        # Females: 100 Approved (50% rate) / 100 Denied (50% rate)
        'Loan_Status': [1] * 600 + [0] * 200 + [1] * 100 + [0] * 100 
    }
    return pd.DataFrame(data)

# Test 1: Severe Representation Bias Detection
def test_1_representation_severe(loan_data):
    results = BiasAnalyzer.analyze_representation_bias(loan_data, 'Gender')
    
    assert results['min_group'] == 'Female'
    assert results['min_percent'] == 20.0 
    assert results['severity'] == "MODERATE" # 20% falls into MODERATE, not SEVERE (<10%)
    
    # Test case for SEVERE (<10%):
    data_severe = pd.DataFrame({'Race': ['White'] * 95 + ['Black'] * 5})
    results_severe = BiasAnalyzer.analyze_representation_bias(data_severe, 'Race')
    assert results_severe['severity'] == "SEVERE"
    assert "severely underrepresented" in results_severe['warning']

# Test 2: Outcome Bias (Disparate Impact Ratio - DIR) Detection
def test_2_outcome_bias_dir_detection(loan_data):
    # Expected: Privileged Rate (Male) = 75% (0.75), Unprivileged Rate (Female) = 50% (0.50)
    # Expected DIR = 0.50 / 0.75 = 0.666
    # 0.666 is below the 0.80 lower threshold -> SEVERE bias detected against Female
    
    results = BiasAnalyzer._calculate_disparate_impact_ratio(
        loan_data, 
        target_col='Loan_Status', 
        sensitive_col='Gender', 
        positive_label=1
    )
    
    assert results['privileged_group'] == 'Male'
    assert results['unprivileged_group'] == 'Female'
    assert results['dir_ratio'] == pytest.approx(0.6667, abs=1e-3)
    assert results['severity'] == "SEVERE"
    assert "Outcome bias detected against 'Female'" in results['warning']

# Test 3: No Bias Detected (DIR near 1.0)
def test_3_no_bias_detected():
    # Males (80%) Rate: 600/800 = 75%
    # Females (20%) Rate: 150/200 = 75%
    data = {
        'Gender': ['Male'] * 800 + ['Female'] * 200,
        'Loan_Status': [1] * 600 + [0] * 200 + [1] * 150 + [0] * 50 
    }
    df = pd.DataFrame(data)
    results = BiasAnalyzer._calculate_disparate_impact_ratio(
        df, 'Loan_Status', 'Gender', positive_label=1
    )
    
    assert results['dir_ratio'] == 1.0
    assert results['severity'] == "LOW"
    assert results['warning'] is None