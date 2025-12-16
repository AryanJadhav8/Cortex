import pandas as pd
from typing import List

class BiasAnalyzer:
    """
    Analyzes dataset for Representation Bias and Outcome/Label Bias 
    by comparing statistical metrics across sensitive attributes.
    """
    
    # Thresholds for Disparate Impact Ratio (DIR)
    # DIR outside of [0.8, 1.25] is generally considered statistically significant disparate impact
    DIR_THRESHOLD_LOWER = 0.80
    DIR_THRESHOLD_UPPER = 1.25

    @staticmethod
    def _calculate_disparate_impact_ratio(df: pd.DataFrame, target_col: str, sensitive_col: str, positive_label: any) -> dict:
        """
        Calculates the Disparate Impact Ratio (DIR) for binary classification problems.
        DIR = (Rate of Positive Outcome for Unprivileged Group) / (Rate of Positive Outcome for Privileged Group)
        """
        try:
            # Drop NaNs for a clean count of groups
            df_clean = df[[sensitive_col, target_col]].dropna()
            
            # Identify the two main groups (assuming binary sensitive attribute for simplicity)
            group_counts = df_clean[sensitive_col].value_counts()
            if len(group_counts) < 2:
                return {"error": f"Not enough groups for DIR in {sensitive_col}"}

            # For the purpose of this analysis, we define the "Privileged" group as the LARGEST group
            # and the "Unprivileged" group as the SMALLEST group.
            privileged_group = group_counts.index[group_counts.argmax()]
            unprivileged_group = group_counts.index[group_counts.argmin()]

            # Calculate the positive outcome rate (Selection Rate) for each group
            # Filter for rows where the target column matches the positive label
            
            # Privileged Rate (RP)
            df_priv = df_clean[df_clean[sensitive_col] == privileged_group]
            rate_priv = (df_priv[target_col] == positive_label).mean()
            
            # Unprivileged Rate (RU)
            df_unpriv = df_clean[df_clean[sensitive_col] == unprivileged_group]
            rate_unpriv = (df_unpriv[target_col] == positive_label).mean()
            
            # Avoid division by zero
            if rate_priv == 0:
                dir_ratio = float('inf') if rate_unpriv > 0 else 1.0
            else:
                dir_ratio = rate_unpriv / rate_priv
                
            severity = "LOW"
            warning = None

            if dir_ratio < BiasAnalyzer.DIR_THRESHOLD_LOWER:
                severity = "SEVERE"
                warning = f"Outcome bias detected against '{unprivileged_group}'. Unprivileged group's success rate is {dir_ratio:.2f}x that of the privileged group. This is considered statistically disparate impact."
            elif dir_ratio > BiasAnalyzer.DIR_THRESHOLD_UPPER:
                severity = "MODERATE"
                warning = f"Outcome bias detected in favor of '{unprivileged_group}'. Unprivileged group's success rate is {dir_ratio:.2f}x that of the privileged group."

            return {
                "privileged_group": str(privileged_group),
                "unprivileged_group": str(unprivileged_group),
                "privileged_rate": round(rate_priv, 4),
                "unprivileged_rate": round(rate_unpriv, 4),
                "dir_ratio": round(dir_ratio, 4),
                "severity": severity,
                "warning": warning
            }
        
        except Exception as e:
            return {"error": f"Failed to calculate DIR: {e}"}

    # In src/core/bias.py:

    @staticmethod
    def analyze_representation_bias(df: pd.DataFrame, sensitive_col: str) -> dict:
        """
        Analyzes the column for unequal representation (Representation Bias).
        """
        counts = df[sensitive_col].value_counts(normalize=True).round(4) * 100
        total = len(df)
        
        min_percent = counts.min()
        min_group = counts.index[counts.argmin()]
        
        severity = "LOW"
        warning = None
        
        if min_percent < 10: # If any group is < 10%
            severity = "SEVERE"
            warning = f"Representation bias: Group '{min_group}' is severely underrepresented, making up only {min_percent:.2f}% of the dataset. This increases the risk of poor generalization."
        elif min_percent <= 20: # FIX: Include 20% to trigger MODERATE warning
            severity = "MODERATE"
            warning = f"Representation bias: Group '{min_group}' is underrepresented ({min_percent:.2f}%). Consider sampling methods to increase representation."

        return {
            "distribution_percent": counts.to_dict(),
            "min_group": str(min_group),
            "min_percent": round(min_percent, 2),
            "severity": severity,
            "warning": warning
        }


    @staticmethod
    def run_bias_analysis(df: pd.DataFrame, target_col: str, sensitive_cols: List[str], positive_label: any = 1) -> dict:
        """
        Main runner function to execute both types of bias analysis.
        """
        results = {}
        for col in sensitive_cols:
            if col not in df.columns:
                continue

            analysis = {
                "representation": BiasAnalyzer.analyze_representation_bias(df, col)
            }
            
            # Only run Outcome Bias for classification targets (assuming binary for now)
            # Check if target is binary (2 unique values) and the column is not the target itself
            if target_col in df.columns and df[target_col].nunique() == 2 and not df[col].nunique() < 2:
                 # Attempt to infer the positive label if not provided
                if positive_label is None:
                    # Assume the higher numeric label (e.g., 1 over 0) or the label that appears second alphabetically
                    unique_labels = sorted(df[target_col].unique())
                    positive_label = unique_labels[-1]
                    
                analysis["outcome"] = BiasAnalyzer._calculate_disparate_impact_ratio(df, target_col, col, positive_label)
            
            results[col] = analysis
            
        return results