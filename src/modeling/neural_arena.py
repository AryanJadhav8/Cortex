import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

class NeuralArena:
    COMPETITORS = {
        "Logistic Regression": {
            "name": "Logistic Regression",
            "title": "Linear Probability Mapping",
            "description": "Fast baseline model using linear decision boundaries",
            "icon": "Activity",
            "color": "emerald"
        },
        "Random Forest": {
            "name": "Random Forest",
            "title": "Bootstrap Aggregation Ensemble",
            "description": "Great for complex, non-linear patterns through ensemble voting",
            "icon": "Trees",
            "color": "green"
        },
        "Gradient Boosting": {
            "name": "Gradient Boosting",
            "title": "Sequential Error Optimization",
            "description": "Learns from its own mistakes through sequential improvement",
            "icon": "Cpu",
            "color": "amber"
        },
        "SVM": {
            "name": "SVM",
            "title": "High-Dimensional Hyperplane",
            "description": "Finds the optimal boundary between classes in high dimensions",
            "icon": "Target",
            "color": "orange"
        },
        "KNN": {
            "name": "KNN",
            "title": "Local Feature Proximity",
            "description": "Looks at similar data points to make predictions",
            "icon": "Network",
            "color": "cyan"
        }
    }

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
    def run_arena(df: pd.DataFrame, target_col: str, schema: dict) -> dict:
        """Run the Neural Arena competition with 5 competitors"""
        try:
            df_copy = df.copy()
            X = df_copy.drop(columns=[target_col])
            y = df_copy[target_col]

            numerical_cols = [c for c in schema['numeric'] if c in X.columns]
            categorical_cols = [c for c in schema['categorical'] if c in X.columns]

            preprocessor = NeuralArena._create_preprocessing_pipeline(numerical_cols, categorical_cols)

            # Define competitors
            models = {
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
                "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
                "SVM": SVC(kernel='rbf', random_state=42),
                "KNN": KNeighborsClassifier(n_neighbors=5)
            }

            results = {}
            best_model_name = None
            best_accuracy = 0

            # Use Stratified K-Fold for robust evaluation
            skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

            for model_name, model in models.items():
                try:
                    pipeline = Pipeline(steps=[
                        ('preprocessor', preprocessor),
                        ('model', model)
                    ])

                    # Get stratified cross-validation scores
                    cv_scores = cross_val_score(pipeline, X, y, cv=skf, scoring='accuracy')
                    accuracy = cv_scores.mean()
                    std_dev = cv_scores.std()

                    results[model_name] = {
                        "accuracy": float(accuracy),
                        "accuracy_pct": f"{accuracy * 100:.1f}%",
                        "std_dev": float(std_dev),
                        "cv_scores": [float(score) for score in cv_scores],
                        "title": NeuralArena.COMPETITORS[model_name]["title"],
                        "description": NeuralArena.COMPETITORS[model_name]["description"],
                        "icon": NeuralArena.COMPETITORS[model_name]["icon"],
                        "color": NeuralArena.COMPETITORS[model_name]["color"]
                    }

                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_model_name = model_name

                except Exception as e:
                    results[model_name] = {
                        "accuracy": 0.0,
                        "accuracy_pct": "0.0%",
                        "std_dev": 0.0,
                        "cv_scores": [],
                        "title": NeuralArena.COMPETITORS[model_name]["title"],
                        "description": NeuralArena.COMPETITORS[model_name]["description"],
                        "error": str(e)
                    }

            # Sort by accuracy (descending)
            sorted_results = dict(sorted(results.items(), key=lambda x: x[1]["accuracy"], reverse=True))

            return {
                "arena_results": sorted_results,
                "champion": {
                    "name": best_model_name,
                    "accuracy": f"{best_accuracy * 100:.1f}%",
                    "title": NeuralArena.COMPETITORS[best_model_name]["title"] if best_model_name else "None"
                },
                "total_competitors": len(models)
            }

        except Exception as e:
            return {"error": str(e), "arena_results": {}, "champion": {}}