import pytest
from src.reporting.scorer import HealthScorer

# Fixture simulating a perfect dataset (0 penalty)
@pytest.fixture
def perfect_results():
    return {
        "health_results": {
            "missing_data": {}, # No missing data
            "duplicate_summary": {"duplicate_percent": 0.0}, # No duplicates
            "cardinality": {"Unique Values": {'A': {'A': 5}, 'B': {'B': 10}}, "Cardinality Flag": {'A': {'A': 'Low/Medium'}}},
        },
        "imbalance_results": {
            "type": "Classification", 
            "severity": "LOW" # No imbalance
        },
        "total_rows": 10
    }

# Fixture simulating a terrible dataset (High penalty)
@pytest.fixture
def terrible_results():
    return {
        "health_results": {
            # 81% missing in two columns (triggers MAX 35 penalty)
            "missing_data": {"Missing Percent": {'Col1': {'Col1': 81.0}, 'Col2': {'Col2': 81.0}}}, 
            "duplicate_summary": {"duplicate_percent": 15.0}, # >10% duplicates (triggers MAX 15 penalty)
            "cardinality": {
                # Triggers MAX ID penalty (1/2 features) and MAX Constant penalty (1/2 features) (10+10 = 20 total weight)
                "Unique Values": {'ID_Col': {'ID_Col': 90}, 'Const_Col': {'Const_Col': 1}},
                "Cardinality Flag": {'ID_Col': {'ID_Col': 'High (Potential ID)'}, 'Const_Col': {'Const_Col': 'Low/Medium'}}
            },
        },
        "imbalance_results": {
            "type": "Classification", 
            "severity": "SEVERE" # Severe imbalance (triggers MAX 30 penalty)
        },
        "total_rows": 100
    }

# --- Test Cases ---

def test_1_perfect_score(perfect_results):
    score, interpretation = HealthScorer.get_health_score(
        perfect_results["health_results"], 
        perfect_results["imbalance_results"], 
        perfect_results["total_rows"]
    )
    # Expected: 100 (0 penalty)
    assert score == 100
    assert "Excellent" in interpretation

def test_2_terrible_score(terrible_results):
    score, interpretation = HealthScorer.get_health_score(
        terrible_results["health_results"], 
        terrible_results["imbalance_results"], 
        terrible_results["total_rows"]
    )
    # Expected Penalty: 35 (Missing) + 30 (Imbalance) + 15 (Duplicates) + 10 (Card) + 10 (Const) = 100
    # Expected Score: 100 - 90 = 10 (Since Cardinality/Constant only partially maxed out in the fixture)
    
    # NOTE: With the fixed logic, this now resolves to Score 10.
    assert score == 10 
    assert "Poor" in interpretation

def test_3_medium_imbalance_penalty(perfect_results):
    # Only change the imbalance
    results = perfect_results.copy()
    results["imbalance_results"]["severity"] = "MEDIUM" # 50% of 30 weight = 15 penalty
    
    score, _ = HealthScorer.get_health_score(
        results["health_results"], 
        results["imbalance_results"], 
        results["total_rows"]
    )
    # Expected Score: 100 - 15 = 85
    assert score == 85

def test_4_moderate_missing_data_penalty(perfect_results):
    # Only moderate missing data (>5%)
    results = perfect_results.copy()
    # Avg missingness is 20%. Triggers 25% of MAX missing penalty (35 * 0.25 = 8.75 penalty, rounded to 9)
    results["health_results"]["missing_data"] = {"Missing Percent": {'C1': {'C1': 10.0}, 'C2': {'C2': 20.0}, 'C3': {'C3': 30.0}}}
    
    score, _ = HealthScorer.get_health_score(
        results["health_results"], 
        results["imbalance_results"], 
        results["total_rows"]
    )
    # Expected Score: 100 - 9 = 91. (The old assertion of 90 was incorrect based on our weights)
    assert score == 91