from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from src.modeling.baseline import BaselineModeler
from src.core.remediator import DataRemediator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/heal")
async def heal_data(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    # 1. Calculate Health Data (Missing per column)
    health_map = {k: int(v) for k, v in df.isnull().sum().to_dict().items() if v > 0}
    if not health_map: health_map = {col: 0 for col in df.columns[:5]}

    # 2. Heal Data
    target_col = df.columns[-1]
    healed_df = DataRemediator.smart_impute(df, target_col)
    
    # 3. Run Modeler
    schema = {
        "numeric": healed_df.select_dtypes(include=['number']).columns.tolist(),
        "categorical": healed_df.select_dtypes(include=['object']).columns.tolist()
    }
    model_results = BaselineModeler.run_baseline_model(healed_df, target_col, schema, True)

    # 4. Final Response Construction (Ensures report.stats exists)
    return {
        "stats": {
            "accuracy": model_results["accuracy"],
            "missing_before": model_results["missing_before"],
            "rows": model_results["rows"]
        },
        "analysis": {
            "health_data": health_map,
            "feature_importance": model_results["feature_importance"]
        },
        "preview_data": healed_df.head(10).to_dict(orient="records")
    }