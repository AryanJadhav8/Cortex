import pandas as pd
import numpy as np

class ImbalanceAnalyzer:
    """
    Analyzes the distribution of the target variable (classification or regression)
    to detect imbalance, skewness, or potential outliers.
    """
    
    # Thresholds for classification imbalance severity (ratio of minority/majority class)
    # 0.10 -> Severe (10% or less minority class)
    # 0.25 -> Medium (25% or less minority class)
    CLASSIFICATION_THRESHOLDS = {
        "SEVERE": 0.10,
        "MEDIUM": 0.25
    }

    # Thresholds for regression skewness severity (absolute value of skew)
    REGRESSION_THRESHOLDS = {
        "HIGH": 1.0, # Highly skewed, requires log/root transformation
        "MEDIUM": 0.5 # Moderately skewed, may require transformation
    }

    @staticmethod
    def analyze_classification_target(df: pd.DataFrame, target_col: str) -> dict:
        """
        Analyzes the target column for class imbalance.
        """
        counts = df[target_col].value_counts()
        total = len(df)
        
        if len(counts) < 2:
            return {"type": "Classification", "status": "Single Class Detected."}
            
        # Determine Imbalance Ratio (Smallest count / Largest count)
        majority_count = counts.max()
        minority_count = counts.min()
        imbalance_ratio = round(minority_count / majority_count, 4) 
        
        severity = "LOW"
        if imbalance_ratio <= ImbalanceAnalyzer.CLASSIFICATION_THRESHOLDS["SEVERE"]:
            severity = "SEVERE"
        elif imbalance_ratio <= ImbalanceAnalyzer.CLASSIFICATION_THRESHOLDS["MEDIUM"]:
            severity = "MEDIUM"

        # Generate a human-readable warning
        warning_msg = f"Minority class ratio is {imbalance_ratio*100:.2f}%. Severity: {severity}."
        if severity != "LOW":
            warning_msg += " Model performance will likely suffer on the minority class."

        return {
            "type": "Classification",
            "distribution": counts.to_dict(),
            "distribution_percent": (counts / total * 100).round(2).to_dict(),
            "minority_class": counts.index[counts.argmin()],
            "imbalance_ratio": imbalance_ratio,
            "severity": severity,
            "warning": warning_msg
        }
        
    @staticmethod
    def analyze_regression_target(df: pd.DataFrame, target_col: str) -> dict:
        """
        Analyzes a numerical target for high skewness (for regression).
        """
        data = df[target_col].dropna()
        if data.empty:
            return {"type": "Regression", "status": "Target column is empty."}
            
        skewness = data.skew()
        
        skew_severity = "LOW"
        if abs(skewness) > ImbalanceAnalyzer.REGRESSION_THRESHOLDS["HIGH"]: 
            skew_severity = "HIGH"
        elif abs(skewness) > ImbalanceAnalyzer.REGRESSION_THRESHOLDS["MEDIUM"]: 
            skew_severity = "MEDIUM"
        
        # Outlier Detection (simple IQR method for context)
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        upper_outliers = data[data > (Q3 + 1.5 * IQR)].count()
        lower_outliers = data[data < (Q1 - 1.5 * IQR)].count()
        
        warning_msg = f"Target distribution skewness is {skewness:.2f} ({skew_severity})."
        if skew_severity == "HIGH":
            warning_msg += " HIGH skew suggests considering log/root transformation."

        return {
            "type": "Regression",
            "skewness": round(skewness, 2),
            "outlier_count": upper_outliers + lower_outliers,
            "skew_severity": skew_severity,
            "warning": warning_msg
        }

   # In src/core/imbalance.py

    @staticmethod
    def run_imbalance_analysis(df: pd.DataFrame, target_col: str, target_is_numeric: bool) -> dict:
        """
        Main runner function to decide between classification and regression analysis.
        """
        try:
            if target_is_numeric:
                # Assumes analyze_regression_target returns a dict
                return ImbalanceAnalyzer.analyze_regression_target(df, target_col)
            else:
                # Assumes analyze_classification_target returns a dict
                return ImbalanceAnalyzer.analyze_classification_target(df, target_col)
        
        except Exception as e:
            # 🚨 CRITICAL FIX: Always return a dictionary on failure
            # This prevents the HealthScorer from receiving a float or non-dictionary value.
            return {"error": f"Imbalance analysis failed in target type routing: {e}",
                    "severity": "CRITICAL",
                    "imbalance_ratio": 0.0,
                    "warning": f"Imbalance analysis could not be completed. Error: {e}"}