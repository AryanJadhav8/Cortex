import pandas as pd
import numpy as np
import traceback
from sklearn.impute import KNNImputer

class DataRemediator:
    @staticmethod
    def smart_impute(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Heals missing values while preserving text columns (like Names).
        """
        try:
            df_healed = df.copy()
            
            # 1. Separate Columns by type
            # We only want to run KNN on numbers. We leave 'object' (text) alone.
            numeric_cols = df_healed.select_dtypes(include=[np.number]).columns.tolist()
            text_cols = df_healed.select_dtypes(exclude=[np.number]).columns.tolist()

            # 2. Heal Numeric Columns
            if numeric_cols:
                # We use KNN only on the numeric part
                imputer = KNNImputer(n_neighbors=min(5, len(df)-1))
                
                # Perform the imputation
                imputed_numeric = imputer.fit_transform(df_healed[numeric_cols])
                
                # Put the healed numbers back
                df_healed[numeric_cols] = imputed_numeric

                # 3. SAFETY NET: If KNN left any NaNs (the '2' you saw), use Median
                if df_healed[numeric_cols].isnull().sum().sum() > 0:
                    df_healed[numeric_cols] = df_healed[numeric_cols].fillna(df_healed[numeric_cols].median())

            # 4. Heal Text Columns (Keep them as text!)
            for col in text_cols:
                # Instead of numbers, we just fill empty names with "Unknown"
                df_healed[col] = df_healed[col].fillna("Unknown")

            return df_healed

        except Exception as e:
            print(f"DEBUG ERROR: {traceback.format_exc()}")
            return df