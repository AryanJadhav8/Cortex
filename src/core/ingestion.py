from typing import Dict, List, Any
import pandas as pd
import io
from collections import Counter # Keep this for robust duplicate counting

class DataLoader:
    """
    Handles secure loading and initial validation of CSV datasets.
    """
    
    @staticmethod
    def load_file(file_buffer) -> pd.DataFrame:
        """
        Reads a CSV file buffer into a Pandas DataFrame with strict validation.
        
        ... (omitted docstring for brevity) ...
        """
        try:
            # --- Preparation: Reset file pointer ---
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            
            # 1. Read the file without using the header row initially (header=None)
            # This allows us to check the raw header before Pandas renames it.
            temp_df = pd.read_csv(file_buffer, header=None)
            
            if temp_df.empty:
                raise ValueError("The uploaded dataset is empty.")

            # Extract the raw column names from the first row (index 0)
            raw_column_names = [str(x).strip() for x in temp_df.iloc[0].tolist()]

            # 2. Check for duplicate column names
            header_counts = Counter(raw_column_names)
            dupes = [name for name, count in header_counts.items() if count > 1]
            if dupes:
                raise ValueError(f"Duplicate column names detected: {dupes}")
            
            # 3. Create the final DataFrame: Set the first row as the actual header and drop it
            df = temp_df[1:].copy()
            df.columns = raw_column_names

            # 4. Final checks
            if df.empty:
                raise ValueError("The uploaded dataset is empty.")
            
            # 5. Standardize column names (stripping was done above, but good practice)
            df.columns = df.columns.str.strip()
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("The file appears to be empty or not a valid CSV.")
        except Exception as e:
            # Re-raise known exceptions
            if "Duplicate column" in str(e) or "empty" in str(e):
                raise e
            # For debugging, we re-raise unknown errors
            raise ValueError(f"Failed to parse CSV: {str(e)}")


    @staticmethod
    def infer_schema(df: pd.DataFrame, target_col: str) -> Dict[str, Any]: # <-- MUST BE DEFINED LIKE THIS
        """
        Infers the data type categories (numeric, categorical, datetime) for features.
        """
        numeric_cols: List[str] = []
        categorical_cols: List[str] = []
        datetime_cols: List[str] = []
        # new: capture numeric columns that are actually binary categorical (e.g., 0/1 flags)
        binary_categorical: List[str] = []

        # Determine unique value count threshold for categorical features
        # Assuming any column with <= 50 unique values OR < 10% of total rows is treated as categorical/object
        max_categorical_cardinality = min(50, int(len(df) * 0.1))

        for col in df.columns:
            if col == target_col:
                continue

            # Check for Datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.append(col)

            # Check for Numeric
            elif pd.api.types.is_numeric_dtype(df[col]):
                # Check whether a numeric column is actually binary (two unique non-null values)
                try:
                    unique_nonnull = df[col].dropna().nunique()
                except Exception:
                    unique_nonnull = df[col].nunique()

                if unique_nonnull == 2:
                    binary_categorical.append(col)
                else:
                    numeric_cols.append(col)

            # Remaining are treated as Categorical/Text
            else:
                # If unique count is low, force to categorical
                if df[col].nunique() <= max_categorical_cardinality:
                    categorical_cols.append(col)
                # For high cardinality strings, we treat them as identifiers or noise for now
                else:
                    # Treat high-cardinality strings as categorical but they will be excluded from
                    # most simple modeling/profiling steps to avoid memory issues.
                    # We still track them under 'categorical' but note their high cardinality elsewhere.
                    categorical_cols.append(col)

        # Add the target column back into its respective category. If the target is numeric
        # but binary (e.g., 0/1), classify it as binary_categorical so downstream modules
        # treat it as classification.
        if target_col in df.columns:
            if pd.api.types.is_numeric_dtype(df[target_col]):
                try:
                    target_unique = df[target_col].dropna().nunique()
                except Exception:
                    target_unique = df[target_col].nunique()

                if target_unique == 2:
                    binary_categorical.append(target_col)
                else:
                    numeric_cols.append(target_col)
            else:
                categorical_cols.append(target_col)

        return {
            'numeric': numeric_cols, # No longer filtering out target_col here
            'categorical': categorical_cols, # No longer filtering out target_col here
            'datetime': datetime_cols,
            'binary_categorical': binary_categorical,
            'target': target_col
        }