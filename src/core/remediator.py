import pandas as pd
import numpy as np
import traceback
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder

class DataRemediator:
    @staticmethod
    def smart_impute(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Intelligently fills missing values using KNN.
        """
        try:
            df_healed = df.copy()
            
            # 1. Identify target and features
            # Drop target temporarily to avoid using it to predict missing feature values
            y_temp = df_healed[target_col]
            X_temp = df_healed.drop(columns=[target_col])

            # 2. Identify which columns actually have NaNs
            cols_with_nan = X_temp.columns[X_temp.isnull().any()].tolist()
            if not cols_with_nan:
                return df

            # 3. KNN only works on numbers. We must encode objects temporarily.
            label_encoders = {}
            for col in X_temp.select_dtypes(include=['object', 'category']).columns:
                le = LabelEncoder()
                # We fill NaNs with a placeholder string so LabelEncoder doesn't crash
                X_temp[col] = X_temp[col].astype(str).replace('nan', 'Unknown')
                X_temp[col] = le.fit_transform(X_temp[col])
                label_encoders[col] = le

            # 4. Apply KNN Imputer
            # Using 3 neighbors for a small test dataset
            imputer = KNNImputer(n_neighbors=min(3, len(df)-1))
            imputed_array = imputer.fit_transform(X_temp)
            
            # 5. Reconstruct the DataFrame
            X_healed = pd.DataFrame(imputed_array, columns=X_temp.columns, index=X_temp.index)
            
            # Join target back
            df_final = pd.concat([X_healed, y_temp], axis=1)
            
            return df_final

        except Exception as e:
            print(f"DEBUG ERROR: {traceback.format_exc()}")
            return df