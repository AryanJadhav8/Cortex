import pandas as pd
import numpy as np

class DataHealth:
    """
    Performs a comprehensive health check on the dataset, reporting missingness,
    duplicates, and key column statistics.
    """

    @staticmethod
    def get_missing_data_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the count and percentage of missing values per column.
        
        Returns:
            pd.DataFrame: A summary table of missing data.
        """
        missing_count = df.isnull().sum()
        missing_percent = (missing_count / len(df)) * 100
        
        missing_df = pd.DataFrame({
            'Missing Count': missing_count,
            'Missing Percent': missing_percent.round(2)
        }).sort_values(by='Missing Count', ascending=False)
        
        # Filter to only show columns with missing data
        missing_df = missing_df[missing_df['Missing Count'] > 0]
        
        return missing_df

    @staticmethod
    def get_duplicate_summary(df: pd.DataFrame) -> dict:
        """
        Calculates the total count of duplicate rows.
        
        Returns:
            dict: A summary dictionary.
        """
        total_duplicates = df.duplicated().sum()
        total_rows = len(df)
        
        return {
            "total_rows": total_rows,
            "duplicate_rows": total_duplicates,
            "duplicate_percent": round((total_duplicates / total_rows) * 100, 2) if total_rows > 0 else 0
        }

    @staticmethod
    def get_column_cardinality(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the unique value count (cardinality) for each column.
        
        Returns:
            pd.DataFrame: A summary table of column cardinality.
        """
        cardinality = df.nunique()
        
        cardinality_df = pd.DataFrame({
            'Unique Values': cardinality
        }).sort_values(by='Unique Values', ascending=False)
        
        # Add a flag to identify high-cardinality (potential ID or text) columns
        # Heuristic: If unique values are >90% of rows, flag it.
        cardinality_df['Cardinality Flag'] = np.where(
            cardinality_df['Unique Values'] > (len(df) * 0.9),
            'High (Potential ID)',
            'Low/Medium'
        )
        
        return cardinality_df

    @staticmethod
    def run_health_check(df: pd.DataFrame) -> dict:
        """
        Runs all health checks and combines results into a single dictionary.
        """
        # Note: We convert to_dict() for easy serialization/passing to Streamlit later
        return {
            "missing_data": DataHealth.get_missing_data_summary(df).to_dict(),
            "duplicate_summary": DataHealth.get_duplicate_summary(df),
            "cardinality": DataHealth.get_column_cardinality(df).to_dict()
        }