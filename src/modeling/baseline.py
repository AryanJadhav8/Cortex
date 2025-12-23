import pandas as pd
import numpy as np
import shap
import traceback
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer 
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

class BaselineModeler:
    """
    Builds a simple, robust baseline model using cross-validation to assess 
    data leakage, predictive potential, and SHAP feature importance.
    """

    @staticmethod
    def _create_preprocessing_pipeline(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
        """Creates the ColumnTransformer pipeline for standardizing and encoding features."""
        
        # 1. Numerical Pipeline: Impute median and Scale
        numerical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')), 
            ('scaler', StandardScaler())
        ])
        
        # 2. Categorical Pipeline: Impute 'missing' and One-Hot Encode
        categorical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')), 
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        # 3. Combined Preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_pipeline, numerical_cols),
                ('cat', categorical_pipeline, categorical_cols)
            ],
            remainder='drop'
        )
        return preprocessor

    @staticmethod
    def _get_feature_importances(model: Pipeline, preprocessor: ColumnTransformer, numerical_cols: list, categorical_cols: list) -> dict:
        """Extracts and normalizes traditional feature importances from the model."""
        if not hasattr(model.named_steps['model'], 'feature_importances_'):
            return {} 

        importances = model.named_steps['model'].feature_importances_
        
        # Get feature names after One-Hot Encoding
        ohe_names = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
        all_feature_names = np.concatenate([numerical_cols, ohe_names])
        
        importance_dict = dict(zip(all_feature_names, importances))
        sorted_importance = {k: float(v) for k, v in sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)}
        
        return sorted_importance

    @staticmethod
    def run_baseline_model(df: pd.DataFrame, target_col: str, schema: dict, is_classification: bool) -> dict:
        """
        Runs the full diagnostic pipeline and returns performance metrics + SHAP data.
        """
        try:
            # Defensive copy
            df_copy = df.copy() 
            
            X = df_copy.drop(columns=[target_col])
            y = df_copy[target_col]
            
            numerical_cols = schema['numeric'][:] 
            categorical_cols = schema['categorical'][:] 
            
            if target_col in numerical_cols:
                numerical_cols.remove(target_col)

            preprocessor = BaselineModeler._create_preprocessing_pipeline(numerical_cols, categorical_cols)
            
            # 1. Select Model
            if is_classification:
                base_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
                scoring_metric = 'accuracy'
            else:
                base_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                scoring_metric = 'r2' 

            pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                       ('model', base_model)])

            # 2. Cross-Validation
            cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring=scoring_metric, n_jobs=-1)

            # 3. Final Fit for SHAP and Importance
            pipeline.fit(X, y)
            
            # 4. Extract Feature Names
            ohe_names = pipeline.named_steps['preprocessor'].named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
            all_feature_names = np.concatenate([numerical_cols, ohe_names])

            # 5. SHAP Explanations
            X_transformed = pipeline.named_steps['preprocessor'].transform(X)
            X_transformed_df = pd.DataFrame(X_transformed, columns=all_feature_names)

            explainer = shap.TreeExplainer(pipeline.named_steps['model'])
            shap_results = explainer.shap_values(X_transformed_df)

            # Handle SHAP output variability across versions/tasks
            if is_classification:
                # Random Forest Classifiers return SHAP values for each class [0, 1]
                if isinstance(shap_results, list):
                    shap_values_to_report = shap_results[1]
                    base_val = float(explainer.expected_value[1])
                elif len(shap_results.shape) == 3: # (samples, features, classes)
                    shap_values_to_report = shap_results[:, :, 1]
                    base_val = float(explainer.expected_value[1])
                else:
                    shap_values_to_report = shap_results
                    base_val = float(explainer.expected_value)
            else:
                # Regression
                shap_values_to_report = shap_results
                base_val = float(explainer.expected_value)

            # 6. Final Results assembly
            importances = BaselineModeler._get_feature_importances(pipeline, preprocessor, numerical_cols, categorical_cols)
            mean_cv_score = cv_scores.mean()
            
            return {
                "model_type": "Classification" if is_classification else "Regression",
                "mean_cv_score": round(mean_cv_score, 4),
                "cv_scores": cv_scores.round(4).tolist(),
                "leakage_warning": "SEVERE LEAKAGE DETECTED" if mean_cv_score > 0.99 else None,
                "feature_importances": importances,
                "shap_data": {
                    "values": shap_values_to_report.tolist(),
                    "base_value": base_val,
                    "feature_names": all_feature_names.tolist()
                }
            }

        except Exception:
            return {"error": f"Baseline model or SHAP failed. Details:\n{traceback.format_exc()}"}