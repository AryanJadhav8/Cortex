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
    def infer_schema(df: pd.DataFrame) -> dict:
        """
        Analyzes column types to classify them for downstream analysis.
        Returns a dictionary separating numeric, categorical, and ID-like columns.
        """
        schema = {
            "numeric": [],
            "categorical": [],
            "id_like": [],
            "datetime": []
        }
        
        for col in df.columns:
            # Get distinct count and total count
            n_unique = df[col].nunique()
            total_rows = len(df)
            dtype = df[col].dtype
            
            # Heuristic: If all values are unique and it's a string/int, it's likely an ID
            # But only if the dataset is reasonably large (>50 rows)
            if n_unique == total_rows and total_rows > 50:
                schema["id_like"].append(col)
                continue
                
            # Check Numeric
            if pd.api.types.is_numeric_dtype(dtype):
                schema["numeric"].append(col)
            # Check Datetime
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                schema["datetime"].append(col)
            # Default to Categorical (Object/String)
            else:
                schema["categorical"].append(col)
                
        return schema