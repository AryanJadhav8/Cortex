import pandas as pd
import numpy as np
import shap
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer 
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

class BaselineModeler:
    @staticmethod
    def _create_preprocessing_pipeline(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
        numerical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')), 
            ('scaler', StandardScaler())
        ])
        categorical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')), 
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        return ColumnTransformer(transformers=[
            ('num', numerical_pipeline, numerical_cols),
            ('cat', categorical_pipeline, categorical_cols)
        ], remainder='drop')

    @staticmethod
    def run_baseline_model(df: pd.DataFrame, target_col: str, schema: dict, is_classification: bool) -> dict:
        try:
            df_copy = df.copy() 
            X = df_copy.drop(columns=[target_col])
            y = df_copy[target_col]
            
            numerical_cols = [c for c in schema['numeric'] if c in X.columns]
            categorical_cols = [c for c in schema['categorical'] if c in X.columns]

            preprocessor = BaselineModeler._create_preprocessing_pipeline(numerical_cols, categorical_cols)
            model = RandomForestClassifier(n_estimators=100, random_state=42) if is_classification else RandomForestRegressor(n_estimators=100, random_state=42)
            
            pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
            cv_scores = cross_val_score(pipeline, X, y, cv=5)
            pipeline.fit(X, y)

            # Simplified importance logic to prevent empty objects
            importances = pipeline.named_steps['model'].feature_importances_
            ohe_names = pipeline.named_steps['preprocessor'].named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
            final_names = numerical_cols + ohe_names.tolist()
            
            feat_imp = {final_names[i].split('__')[-1]: float(importances[i]) for i in range(min(len(final_names), len(importances)))}
            feat_imp = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True)[:8])

            return {
                "accuracy": f"{cv_scores.mean() * 100:.1f}%",
                "feature_importance": feat_imp,
                "rows": len(df),
                "missing_before": int(df.isnull().sum().sum())
            }
        except Exception as e:
            return {"accuracy": "0.0%", "feature_importance": {}, "rows": len(df), "missing_before": 0}