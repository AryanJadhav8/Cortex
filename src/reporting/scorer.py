class HealthScorer:
    """
    Calculates a unified Dataset Health Score (0-100) based on weighted penalties
    derived from dataset health and imbalance analysis.
    """

    # Weights for different penalty categories (sum to 100 for maximum impact)
    PENALTY_WEIGHTS = {
        "missing_data": 35,    # High weight: Missing data often requires imputation/dropping
        "imbalance_risk": 30,  # High weight: Imbalance kills model performance
        "duplicate_data": 15,  # Medium weight: Data leakage/training inefficiency
        "cardinality_risk": 10, # Low weight: ID columns (risk for modeling)
        "constant_features": 10 # Low weight: Useless/constant features
    }

    @staticmethod
    def calculate_missing_data_penalty(missing_summary: dict, total_rows: int) -> float:
        """
        Penalizes based on the percentage of missing values.
        
        Uses a stepped approach:
        > 80% missing in ANY column: MAX penalty (35)
        > 40% AVG missing: High penalty (75% of 35)
        > 5% AVG missing: Moderate penalty (25% of 35)
        """
        if not missing_summary:
            return 0.0

        missing_percents = [percent_dict.get(col_name) 
                            for col_name, percent_dict in missing_summary.get('Missing Percent', {}).items()]
        
        if not missing_percents:
            return 0.0
            
        # Rule 1: Catastrophic failure (any column > 80% missing)
        if any(p > 80 for p in missing_percents):
            return HealthScorer.PENALTY_WEIGHTS["missing_data"]

        # Calculate the average missing percentage of affected columns
        avg_missing = sum(missing_percents) / len(missing_percents)
        
        # Rule 2: High or Moderate penalties (based on average impact)
        if avg_missing > 40:
            # High average missingness (40-80%): 75% of max penalty
            return HealthScorer.PENALTY_WEIGHTS["missing_data"] * 0.75
        elif avg_missing > 5:
            # Moderate average missingness (5-40%): 25% of max penalty
            return HealthScorer.PENALTY_WEIGHTS["missing_data"] * 0.25
            
        return 0.0

    @staticmethod
    def calculate_imbalance_penalty(imbalance_analysis: dict) -> float:
        """
        Penalizes based on the imbalance severity detected in the target variable.
        """
        if imbalance_analysis.get('type') != 'Classification':
            return 0.0 # Only penalize classification tasks for imbalance

        severity = imbalance_analysis.get('severity', 'LOW')
        
        if severity == "SEVERE":
            return HealthScorer.PENALTY_WEIGHTS["imbalance_risk"] * 1.0
        elif severity == "MEDIUM":
            return HealthScorer.PENALTY_WEIGHTS["imbalance_risk"] * 0.5
        
        return 0.0

    @staticmethod
    def calculate_duplicate_penalty(duplicate_summary: dict) -> float:
        """
        Penalizes based on the percentage of duplicated rows.
        """
        duplicate_percent = duplicate_summary.get('duplicate_percent', 0.0)
        
        # Max penalty if >10% duplicates
        if duplicate_percent > 10: 
            normalized_penalty = 1.0
        # Medium penalty if >1% duplicates
        elif duplicate_percent > 1: 
            normalized_penalty = 0.5
        else:
            normalized_penalty = 0.0
            
        return normalized_penalty * HealthScorer.PENALTY_WEIGHTS["duplicate_data"]

    @staticmethod
    def calculate_cardinality_penalty(cardinality_summary: dict, total_rows: int) -> float:
        """
        Penalizes for features with high cardinality (potential ID/noise) or constant features.
        
        FIX: Penalty is now based on the proportion of features affected.
        """
        high_cardinality_count = 0
        constant_count = 0
        
        # Total number of columns analyzed
        all_cols_count = len(cardinality_summary.get('Unique Values', {}))
        if all_cols_count == 0:
            return 0.0

        for col_name, flag_dict in cardinality_summary.get('Cardinality Flag', {}).items():
            flag = flag_dict.get(col_name)
            if flag == 'High (Potential ID)':
                high_cardinality_count += 1

        for col_name, count_dict in cardinality_summary.get('Unique Values', {}).items():
            count = count_dict.get(col_name)
            # Check for constant/near-constant features (unique count <= 1)
            if count <= 1:
                constant_count += 1
        
        # Penalty is proportional to the fraction of features that have the issue.
        penalty_id = (high_cardinality_count / all_cols_count) * HealthScorer.PENALTY_WEIGHTS["cardinality_risk"]
        
        penalty_constant = (constant_count / all_cols_count) * HealthScorer.PENALTY_WEIGHTS["constant_features"]

        return penalty_id + penalty_constant


    @staticmethod
    def get_health_score(health_results: dict, imbalance_results: dict, total_rows: int) -> tuple[int, str]:
        """
        Calculates the final score and provides a human-readable interpretation.
        
        Returns:
            (int, str): The final score (0-100) and the interpretation text.
        """
        total_penalty = 0.0
        
        # 1. Missing Data Penalty
        missing_penalty = HealthScorer.calculate_missing_data_penalty(
            health_results.get('missing_data', {}), total_rows
        )
        total_penalty += missing_penalty
        
        # 2. Imbalance Penalty
        imbalance_penalty = HealthScorer.calculate_imbalance_penalty(imbalance_results)
        total_penalty += imbalance_penalty
        
        # 3. Duplicate Penalty
        duplicate_penalty = HealthScorer.calculate_duplicate_penalty(
            health_results.get('duplicate_summary', {})
        )
        total_penalty += duplicate_penalty
        
        # 4. Cardinality & Constant Feature Penalty
        # Note: We pass the raw cardinality summary (which is nested)
        cardinality_penalty = HealthScorer.calculate_cardinality_penalty(
            health_results.get('cardinality', {}), total_rows
        )
        total_penalty += cardinality_penalty

        # Calculate final score
        final_score = max(0, 100 - round(total_penalty))
        
        # Interpret the score
        if final_score >= 90:
            interpretation = "Excellent. This dataset is exceptionally clean and ready for modeling."
        elif final_score >= 70:
            interpretation = "Good. Minor issues detected, manageable with standard preprocessing (imputation, light balancing)."
        elif final_score >= 50:
            interpretation = "Fair. Significant risks (high imbalance or missing data) detected. Requires careful data remediation before modeling."
        else:
            interpretation = "Poor. Critical data issues detected. Modeling is highly discouraged without major data cleaning or feature engineering."

        return final_score, interpretation