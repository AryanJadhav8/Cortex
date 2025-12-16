import pandas as pd
import numpy as np

class DataProfiler:
    """
    Generates detailed descriptive statistics for both numerical and 
    categorical columns based on the inferred schema.
    """

    @staticmethod
    def profile_numerical_features(df: pd.DataFrame, numerical_cols: list) -> dict:
        """
        Computes standard descriptive statistics for numerical columns.
        """
        if not numerical_cols:
            return {}

        stats_df = df[numerical_cols].describe().transpose()
        
        # Add IQR and Skewness
        stats_df['IQR'] = stats_df['75%'] - stats_df['25%']
        stats_df['skewness'] = df[numerical_cols].skew()
        
        return stats_df.round(2).to_dict('index')

    @staticmethod
    def profile_categorical_features(df: pd.DataFrame, categorical_cols: list, max_categories=10) -> dict:
        """
        Computes value counts and frequency for categorical columns.
        """
        if not categorical_cols:
            return {}
            
        categorical_profiles = {}
        
        for col in categorical_cols:
            n_unique = df[col].nunique()
            value_counts = df[col].value_counts(dropna=False)
            
            top_counts = value_counts.head(max_categories)
            
            # Calculate frequency relative to total data points
            total_count = len(df)
            top_frequencies = (top_counts / total_count * 100).round(2)
            
            categorical_profiles[col] = {
                "unique_count": n_unique,
                "top_categories": top_counts.index.tolist(),
                "top_counts": top_counts.tolist(),
                "top_frequencies_pct": top_frequencies.tolist(),
                "is_high_cardinality": n_unique > max_categories * 2
            }
            
        return categorical_profiles

    @staticmethod
    def run_profiling(df: pd.DataFrame, schema: dict) -> dict:
        """
        Runs both numerical and categorical profiling.
        """
        numerical_profile = DataProfiler.profile_numerical_features(df, schema['numeric'])
        categorical_profile = DataProfiler.profile_categorical_features(df, schema['categorical'])
        
        return {
            "numerical": numerical_profile,
            "categorical": categorical_profile
        }