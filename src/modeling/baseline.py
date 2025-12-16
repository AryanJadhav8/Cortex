import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer # <-- FIX: ADDED FOR HANDLING NaNs
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge

class BaselineModeler:
    """
    Builds a simple, robust baseline model using cross-validation to assess 
    data leakage, predictive potential, and feature importance.
    """

    @staticmethod
    def _create_preprocessing_pipeline(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
        """Creates the ColumnTransformer pipeline for standardizing and encoding features."""
        
        # 1. Numerical Pipeline: Impute median and Scale
        numerical_pipeline = Pipeline([
            # FIX: Use SimpleImputer(median) to handle numerical NaNs gracefully
            ('imputer', SimpleImputer(strategy='median')), 
            ('scaler', StandardScaler())
        ])
        
        # 2. Categorical Pipeline: Impute 'missing' and One-Hot Encode
        categorical_pipeline = Pipeline([
            # FIX: Use SimpleImputer(constant) to treat categorical NaNs as their own category
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')), 
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        # 3. Combined Preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_pipeline, numerical_cols),
                ('cat', categorical_pipeline, categorical_cols)
            ],
            remainder='drop',
            n_jobs=-1
        )
        return preprocessor

    @staticmethod
    def _get_feature_importances(model: Pipeline, preprocessor: ColumnTransformer, numerical_cols: list, categorical_cols: list) -> dict:
        """Extracts and normalizes feature importances from the model."""
        
        # For RandomForest, get the feature importances directly
        if hasattr(model.named_steps['model'], 'feature_importances_'):
            importances = model.named_steps['model'].feature_importances_
        # For linear models (if we used them), we would use coefficients
        else:
            # Fallback for models without feature_importances_ (e.g., if we swapped to linear models)
            return {} 

        # Map importances back to original feature names
        
        # 1. Get OneHotEncoded feature names
        # Note: We must ensure the preprocessor is fitted before calling get_feature_names_out
        ohe_names = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
        
        # 2. Combine all feature names
        all_feature_names = np.concatenate([numerical_cols, ohe_names])
        
        # 3. Create importance dictionary and sort
        importance_dict = dict(zip(all_feature_names, importances))
        sorted_importance = {k: float(v) for k, v in sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)}
        
        return sorted_importance

    @staticmethod
    def run_baseline_model(df: pd.DataFrame, target_col: str, schema: dict, is_classification: bool) -> dict:
        """
        Runs the full diagnostic pipeline and returns performance metrics.
        """
        # Defensive copy to avoid modifying the original dataframe
        df_copy = df.copy() 
        
        # Separate features (X) and target (y)
        X = df_copy.drop(columns=[target_col])
        y = df_copy[target_col]
        
        numerical_cols = schema['numeric'][:] # Use slice to create a copy
        categorical_cols = schema['categorical'][:] # Use slice to create a copy
        
        # Remove the target column from the feature list if it was numeric
        if target_col in numerical_cols:
            numerical_cols.remove(target_col)

        preprocessor = BaselineModeler._create_preprocessing_pipeline(numerical_cols, categorical_cols)
        
        # 1. Select the appropriate model
        if is_classification:
            base_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            scoring_metric = 'accuracy'
        else:
            base_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            # Use R2 for easy interpretation of baseline score
            scoring_metric = 'r2' 

        # 2. Build the full pipeline
        pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                   ('model', base_model)])

        # 3. Perform Cross-Validation (5-fold)
        try:
            cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring=scoring_metric, n_jobs=-1)
        except Exception as e:
            # Catch all exceptions during CV, including target type issues or OHE failures
            return {"error": f"Cross-validation failed. Ensure target variable and features are correctly formatted. Error: {e}"}


        # In src/modeling/baseline.py, inside run_baseline_model:

# ... (Up to the point where cv_scores is successfully calculated) ...

# 4. Train the model once on the full dataset to get feature importance
        try:
            pipeline.fit(X, y)
            importances = BaselineModeler._get_feature_importances(pipeline, preprocessor, numerical_cols, categorical_cols)
            
            # 5. Interpret Leakage
            mean_cv_score = cv_scores.mean()
            leakage_warning = None
            
            # Standard warning thresholds (Accuracy > 0.99 or R2 > 0.99)
            if (is_classification and mean_cv_score > 0.99) or (not is_classification and mean_cv_score > 0.99):
                leakage_warning = "SEVERE LEAKAGE DETECTED: CV score is nearly perfect. Data is likely contaminated."

            # 6. Prepare Results (Return the successful dictionary)
            return {
                "model_type": "Classification" if is_classification else "Regression",
                "mean_cv_score": round(mean_cv_score, 4),
                "cv_scores": cv_scores.round(4).tolist(),
                "leakage_warning": leakage_warning,
                "feature_importances": importances
            }

        except Exception as e:
            # This captures any failure during fit, feature importance, or result preparation.
            return {"error": f"Baseline model failed during final fit or feature importance calculation. Error: {e}"}