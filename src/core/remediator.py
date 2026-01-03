import pandas as pd
import numpy as np

class DataRemediator:
    @staticmethod
    def smart_impute(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        df_cleaned = df.copy()

        for col in df_cleaned.columns:
            missing_pct = df_cleaned[col].isnull().mean() * 100
            
            if df_cleaned[col].isnull().any():
                # 1. NUMERIC COLUMNS (Age, Fare, etc.)
                if np.issubdtype(df_cleaned[col].dtype, np.number):
                    # Use median for numbers to avoid outliers affecting the mean
                    df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
                
                # 2. CATEGORICAL COLUMNS (Cabin, Embarked, etc.)
                else:
                    # If more than 50% is missing, don't guess a name. 
                    # Label it as "N/A" so the model knows it's missing data.
                    if missing_pct > 50:
                        df_cleaned[col] = df_cleaned[col].fillna("N/A")
                    else:
                        # Otherwise, use the most frequent value (Mode)
                        mode_val = df_cleaned[col].mode()
                        if not mode_val.empty:
                            df_cleaned[col] = df_cleaned[col].fillna(mode_val[0])
                        else:
                            df_cleaned[col] = df_cleaned[col].fillna("Unknown")
        
        return df_cleaned