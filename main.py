from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from src.modeling.baseline import BaselineModeler
from src.core.remediator import DataRemediator

app = FastAPI(title="CORTEX AI API")

# Allow React to talk to this API later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "CORTEX Online", "features": ["SHAP Interpretability", "KNN Remediation"]}

@app.post("/analyze")
async def analyze_data(file: UploadFile = File(...)):
    try:
        # 1. Load Data
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # 2. Basic Setup (Target is last column for now)
        target_col = df.columns[-1]
        schema = {
            "numeric": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical": df.select_dtypes(include=['object']).columns.tolist()
        }
        
        # 3. Run SHAP Model
        results = BaselineModeler.run_baseline_model(df, target_col, schema, is_classification=True)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/heal")
async def heal_data(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        target_col = df.columns[-1]
        healed_df = DataRemediator.smart_impute(df, target_col)
        
        return {
            "missing_before": int(df.isnull().sum().sum()),
            "missing_after": int(healed_df.isnull().sum().sum()),
            "data": healed_df.head(10).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))