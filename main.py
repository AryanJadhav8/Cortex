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
    selected_columns: str = Form("[]"),
    target_column: str = Form(None)  # ADD THIS LINE
):
    try:
        # 1. READ FILE
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        total_rows = len(df)
        
        # 2. RESOLVE TARGET COLUMN - MODIFY THIS SECTION
        # If frontend sent a target, use it. Otherwise, default to the last column.
        if target_column and target_column in df.columns:
            target_col = target_column
        else:
            target_col = df.columns[-1]

        # 3. PARSE SELECTED COLUMNS
        try:
            chosen_features = json.loads(selected_columns)
        except Exception:
            chosen_features = []

        # If no features are selected, use all columns EXCEPT the target
        if not chosen_features:
            chosen_features = [c for c in df.columns if c != target_col]
        
        # SAFETY CHECK: Remove target from features if it's accidentally there
        if target_col in chosen_features:
            chosen_features.remove(target_col)

        # 4. GENERATE DIAGNOSTICS (Always based on full dataset)
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

        # 5. SMART HEALING
        from src.core.remediator import DataRemediator
        healed_df = DataRemediator.smart_impute(df, target_col)
        
        # 6. MODELING PREPARATION - MODIFY THIS SECTION
        # Build features list + target for modeling
        modeling_cols = chosen_features + [target_col]
        model_input_df = healed_df[modeling_cols]
        
        from src.modeling.baseline import BaselineModeler
        schema = {
            "numeric": model_input_df.select_dtypes(include=['number']).columns.tolist(),
            "categorical": model_input_df.select_dtypes(include=['object']).columns.tolist()
        }
        
        # Remove target from schema to avoid modeler confusion
        if target_col in schema["numeric"]:
            schema["numeric"].remove(target_col)
        if target_col in schema["categorical"]:
            schema["categorical"].remove(target_col)
        
        model_results = BaselineModeler.run_baseline_model(model_input_df, target_col, schema, True)

        # 7. RESPONSE - ADD target_used TO STATS
        return {
            "stats": {
                "accuracy": model_results.get("accuracy", "N/A"),
                "missing_before": int(df.isnull().sum().sum()),
                "rows": total_rows,
                "target_used": target_col  # ADD THIS LINE
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