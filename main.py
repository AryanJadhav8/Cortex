from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
import logging

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/heal")
async def heal_data(
    file: UploadFile = File(...), 
    selected_columns: str = Form("[]") 
):
    try:
        # 1. READ FILE
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        total_rows = len(df)
        target_col = df.columns[-1]

        # 2. PARSE SELECTED COLUMNS
        try:
            chosen_features = json.loads(selected_columns)
        except Exception:
            chosen_features = []

        # 3. GENERATE DIAGNOSTICS (Always based on full dataset)
        column_diagnostics = []
        for col in df.columns:
            unique_count = df[col].nunique()
            missing_count = int(df[col].isnull().sum())
            missing_pct = round((missing_count / total_rows) * 100, 1)
            cardinality_ratio = unique_count / total_rows
            
            column_diagnostics.append({
                "label": col,
                "value": col,
                "cardinality": unique_count,
                "missing_pct": missing_pct,
                "type": str(df[col].dtype),
                "is_noisy": cardinality_ratio > 0.8 and df[col].dtype == 'object'
            })

        # 4. SMART HEALING (Clean the whole dataframe)
        # Assuming DataRemediator is imported correctly
        from src.core.remediator import DataRemediator
        healed_df = DataRemediator.smart_impute(df, target_col)
        
        # 5. MODELING (Filter ONLY for this step)
        # Use all columns if none are selected, otherwise use selection
        features_for_model = chosen_features if chosen_features else df.columns.tolist()
        
        # Ensure target is present for modeling
        if target_col not in features_for_model:
            features_for_model.append(target_col)
            
        model_input_df = healed_df[features_for_model]
        
        from src.modeling.baseline import BaselineModeler
        schema = {
            "numeric": model_input_df.select_dtypes(include=['number']).columns.tolist(),
            "categorical": model_input_df.select_dtypes(include=['object']).columns.tolist()
        }
        
        model_results = BaselineModeler.run_baseline_model(model_input_df, target_col, schema, True)

        return {
            "stats": {
                "accuracy": model_results.get("accuracy", "N/A"),
                "missing_before": int(df.isnull().sum().sum()),
                "rows": total_rows
            },
            "analysis": {
                "health_data": {k: int(v) for k, v in df.isnull().sum().to_dict().items() if v > 0},
                "feature_importance": model_results.get("feature_importance", {}),
                "column_diagnostics": column_diagnostics 
            },
            "preview_data": healed_df.head(10).to_dict(orient="records")
        }
    except Exception as e:
        logging.error(f"Heal error: {str(e)}")
        return {"error": str(e)}, 500