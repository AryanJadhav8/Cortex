import sys
from pathlib import Path

# --- FIX START ---
# Programmatically inject the project root (CORTEX/) into the Python path.
# This ensures imports like 'from src.core...' work when running Streamlit.
# project_root is 3 levels up: generator.py -> reporting -> src -> project_root
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.append(str(project_root))
# --- FIX END ---

import streamlit as st
import pandas as pd

# Import all our core analysis modules (This should now work)
from src.core.ingestion import DataLoader
from src.core.health import DataHealth
from src.core.profiling import DataProfiler
from src.core.imbalance import ImbalanceAnalyzer
from src.reporting.scorer import HealthScorer
from src.modeling.baseline import BaselineModeler
from src.core.bias import BiasAnalyzer

# In src/reporting/generator.py

def run_analysis_pipeline(df: pd.DataFrame, target_col: str, sensitive_cols: list) -> dict:
    """Executes the full CORTEX analysis pipeline with robust error handling."""
    
    analysis_results = {
        "df": df,
        "schema": {},
        "health": {"error": "Module failed to run."},
        "profiling": {"error": "Module failed to run."},
        "imbalance": {"error": "Module failed to run."},
        "bias": {"error": "Module failed to run."},
        "score": 0,
        "interpretation": "Analysis failed in one or more critical steps.",
        "baseline": {"error": "Module failed to run."},
        "target_is_numeric": False
    }

    with st.spinner("Analyzing dataset health..."):
        # In src/reporting/generator.py, inside run_analysis_pipeline:

# ...
        try:
            # 1. Schema Inference (Target is needed for subsequent steps)
            analysis_results['schema'] = DataLoader.infer_schema(df, target_col)

            # --- CRITICAL FIX: Target Type Determination ---
            
            is_in_binary_list = target_col in analysis_results['schema'].get('binary_categorical', [])
            
            # Target is ONLY numeric (Regression) if it's in the numeric list AND NOT in the binary list.
            # For Survived (0/1), is_in_binary_list will be True, making target_is_numeric = False.
            is_in_numeric_list = target_col in analysis_results['schema'].get('numeric', [])

            if is_in_binary_list:
                 analysis_results['target_is_numeric'] = False
            elif is_in_numeric_list:
                 analysis_results['target_is_numeric'] = True
            else:
                # Must be categorical/datetime/unknown (treated as classification)
                analysis_results['target_is_numeric'] = False

        except Exception as e:
# ... (rest of the code is unchanged)
            st.error(f"FATAL: Schema Inference Failed. Cannot proceed. Error: {e}")
            return analysis_results

        # 2. Data Health Check
        try:
            analysis_results['health'] = DataHealth.run_health_check(df)
            total_rows = len(df)
        except Exception as e:
            analysis_results['health']['error'] = f"DataHealth module failed: {e}"
            total_rows = len(df) # Still need total rows

        # 3. Data Profiling
        try:
            analysis_results['profiling'] = DataProfiler.run_profiling(df, analysis_results['schema'])
        except Exception as e:
            analysis_results['profiling']['error'] = f"DataProfiler module failed: {e}"

        # 4. Imbalance Analysis
        try:
            target_is_numeric = analysis_results['target_is_numeric']
            analysis_results['imbalance'] = ImbalanceAnalyzer.run_imbalance_analysis(df, target_col, target_is_numeric)
        except Exception as e:
            analysis_results['imbalance']['error'] = f"ImbalanceAnalyzer module failed: {e}"

        # 5. Bias and Fairness Analysis
        try:
            if sensitive_cols:
                analysis_results['bias'] = BiasAnalyzer.run_bias_analysis(df, target_col, sensitive_cols, positive_label=1)
            else:
                analysis_results['bias'] = {"info": "Bias analysis skipped. No sensitive columns selected."}
        except Exception as e:
            analysis_results['bias']['error'] = f"BiasAnalyzer module failed: {e}"

        # 6. Health Score Calculation (Needs health and imbalance results)
        try:
            score, interpretation = HealthScorer.get_health_score(
                analysis_results['health'], analysis_results['imbalance'], total_rows
            )
            analysis_results['score'] = score
            analysis_results['interpretation'] = interpretation
        except Exception as e:
            analysis_results['score'] = 0
            analysis_results['interpretation'] = f"Score calculation failed: {e}"

        # 7. Baseline Modeling (Diagnostic)
        try:
            # ONLY call baseline if schema inference and imbalance gave dicts (required inputs)
            if 'error' not in analysis_results['schema'] and 'error' not in analysis_results['imbalance']:
                 analysis_results['baseline'] = BaselineModeler.run_baseline_model(
                    df, target_col, analysis_results['schema'], is_classification=(not analysis_results['target_is_numeric'])
                )
            else:
                analysis_results['baseline']['error'] = "Prerequisites for modeling failed."
        except Exception as e:
             analysis_results['baseline']['error'] = f"BaselineModeler module failed unexpectedly: {e}"
    
    return analysis_results

# NOTE: You MUST remove the old run_analysis_pipeline function and replace it with the above.


def render_report(results: dict, target_col: str):
    """Renders the final report using Streamlit components."""
    st.header("🔬 CORTEX Dataset Diagnostic Report")
    
    # --- Section 1: Executive Summary & Score ---
    st.subheader("1. Executive Summary: The CORTEX Score")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Dataset Health Score (0-100)", value=results['score'], delta_color="off")
    
    with col2:
        if results['score'] >= 70:
            st.success(f"**Status:** {results['interpretation']}")
        else:
            st.warning(f"**Status:** {results['interpretation']}")
        
        st.markdown("---")
        dup_percent = results['health']['duplicate_summary']['duplicate_percent']
        if dup_percent > 5:
            st.error(f"⚠️ **High Duplicate Risk:** {dup_percent}% duplicate rows found.")
        elif results['baseline'].get('leakage_warning'):
            st.error(f"🚨 **Model Leakage Detected:** See Section 4.")


    # --- Section 2: Core Data Health ---
    st.header("2. Core Data Health & Integrity")
    
    with st.expander("Integrity Checks (Missingness, Duplicates, Cardinality)", expanded=True):
        st.markdown(f"**Total Rows:** {len(results['df'])} | **Total Features:** {len(results['df'].columns)}")
        
        st.info(f"**Duplicate Rows Found:** {results['health']['duplicate_summary']['duplicate_rows']} ({results['health']['duplicate_summary']['duplicate_percent']}%)")
        
        missing_df = pd.DataFrame(results['health']['missing_data'])
        if not missing_df.empty:
            st.warning("🚨 **Missing Data:** Columns with missing values:")
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.success("✅ No critical missing data found.")
            
        st.subheader("Feature Cardinality Analysis")
        cardinality_raw = results['health'].get('cardinality', {})

        if not cardinality_raw:
            st.info("No cardinality information available for this dataset.")
        else:
            # Support two possible shapes returned from health module:
            # 1) {'Unique Values': {col: count, ...}, 'Cardinality Flag': {...}}
            # 2) {col: {'Unique Values': count, 'Cardinality Flag': flag}, ...}
            try:
                if 'Unique Values' in cardinality_raw:
                    # Orientation 1 -> DataFrame will have index = column names
                    df_card = pd.DataFrame(cardinality_raw)
                else:
                    # Orientation 2 -> build DataFrame with index = column names
                    df_card = pd.DataFrame.from_dict(cardinality_raw, orient='index')

                if 'Unique Values' in df_card.columns:
                    display_df = df_card.sort_values(by='Unique Values', ascending=False)
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("No cardinality information available for this dataset.")
            except Exception as e:
                # Defensive: do not let cardinality render errors crash the app
                st.info("Cardinality could not be computed/displayed.")
                st.debug if hasattr(st, 'debug') else None

    # --- Section 3: Target Variable Imbalance ---
    st.header(f"3. Target Variable Analysis: **{target_col}**")
    
    imbalance = results['imbalance']
    
    if results['target_is_numeric']:
        st.info(f"Regression Target (Numeric). Skewness: **{imbalance['skewness']}** ({imbalance['skew_severity']} Risk)")
        st.warning(imbalance['warning'])
    else:
        st.info(f"Classification Target. Imbalance Ratio (Min/Max): **{imbalance['imbalance_ratio']:.4f}** ({imbalance['severity']} Risk)")
        if imbalance['severity'] != 'LOW':
            st.error(imbalance['warning'])
        
        st.subheader("Class Distribution")
        dist_df = pd.DataFrame({
            "Count": imbalance['distribution'].values(),
            "Percent (%)": imbalance['distribution_percent'].values()
        }, index=imbalance['distribution'].keys())
        st.dataframe(dist_df, use_container_width=True)


    # --- Section 4: Bias and Fairness Analysis (NEW SECTION) ---
    st.header("4. Bias and Fairness Analysis")
    
    bias_results = results['bias']
    # If bias analysis was intentionally skipped, `bias_results` will be a dict with an 'info' key.
    if not bias_results:
        st.info("Please select one or more sensitive attributes to run bias analysis.")
    elif isinstance(bias_results, dict) and 'info' in bias_results:
        st.info(bias_results['info'])
    else:
        for col, analysis in bias_results.items():
            st.subheader(f"Protected Attribute: **{col}**")

            st.markdown("##### Representation Bias")
            rep = analysis.get('representation', {})
            if isinstance(rep, dict):
                if rep.get('severity') == "SEVERE":
                    st.error(f"🚨 **{rep['severity']} Risk:** {rep.get('warning')}")
                elif rep.get('severity') == "MODERATE":
                    st.warning(f"⚠️ **{rep['severity']} Risk:** {rep.get('warning')}")
                else:
                    st.success(f"Representation is balanced (Min Group: {rep.get('min_percent', 'N/A')}%)")
            else:
                st.info(str(rep))

            st.markdown("##### Outcome Bias (Disparate Impact Ratio - DIR)")
            outcome = analysis.get('outcome', {})
            if outcome and isinstance(outcome, dict) and "error" not in outcome:
                dir_ratio = outcome.get('dir_ratio')

                # Check for SEVERE bias (DIR outside 0.8 to 1.25)
                if outcome.get('severity') != 'LOW':
                    st.error(f"🛑 **{outcome.get('severity')} Outcome Bias:** DIR = {dir_ratio}. {outcome.get('warning')}")
                else:
                    st.success(
                        f"✅ Outcome is fair (DIR={dir_ratio}). Rates for '{outcome.get('privileged_group')}' ({outcome.get('privileged_rate')}) and '{outcome.get('unprivileged_group')}' ({outcome.get('unprivileged_rate')}) are statistically similar."
                    )
            elif isinstance(outcome, dict) and "error" in outcome:
                st.info(f"Outcome Bias skipped: {outcome['error']}")


    # --- Section 5: Diagnostic Modeling ---
    # In src/reporting/generator.py, inside render_report(results: dict, target_col: str):

# --- Section 5: Diagnostic Modeling ---
    st.header("5. Diagnostic Modeling & Leakage")

    # FIX START: Ensure baseline is a dictionary before proceeding
    baseline = results['baseline']
    if not isinstance(baseline, dict):
        # This catches cases where an entire dict was replaced by a score or simple error object (float/str)
        st.error(f"Model Run Failed: Unexpected result type. Cannot proceed with modeling report.")
        st.info(f"The raw value returned was: {baseline}")
        return # Exit this section of the report

    # Original error check (this should now work)
    if "error" in baseline:
        st.error(f"Model Run Failed: {baseline['error']}")
    else:
    # FIX END
        st.subheader(f"Baseline Score ({'Accuracy' if not results['target_is_numeric'] else 'R2'})")
        
        # ... rest of Section 5 code remains the same ...
        
        leak_col1, leak_col2 = st.columns(2)

        with leak_col1:
            st.metric(label=f"Mean Cross-Validation Score (CV=5)", value=baseline['mean_cv_score'])

        with leak_col2:
            if baseline['leakage_warning']:
                st.error(f"🚨 **LEAKAGE WARNING:** {baseline['leakage_warning']}")
            else:
                st.success("✅ Baseline performance suggests no severe data leakage.")

        st.subheader("Top Feature Importances (Random Forest)")
        importance_df = pd.DataFrame.from_dict(
            baseline['feature_importances'], 
            orient='index', 
            columns=['Importance Score']
        )
        st.dataframe(importance_df.head(10), use_container_width=True)


def main_app():
    st.set_page_config(layout="wide", page_title="CORTEX Dataset Analyzer")

    st.title("CORTEX: Data Integrity Diagnostic")
    st.markdown("Upload your CSV dataset to generate a comprehensive quality report and health score (0-100).")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully. First 5 rows:")
            st.dataframe(df.head(), use_container_width=True)
            
            all_columns = df.columns.tolist()
            
            # User input for Target Column
            target_col = st.selectbox("1. Select the Target (Label) Column for Analysis:", all_columns)

            # User input for Sensitive Columns (for Bias Analysis)
            sensitive_cols = st.multiselect(
                "2. Select Sensitive/Protected Attributes for Bias Analysis (e.g., Gender, Race):",
                all_columns,
                default=[] # Start with no default selection
            )

            if st.button("Run Full CORTEX Analysis"):
                # Run the pipeline and render the results
                results = run_analysis_pipeline(df, target_col, sensitive_cols)
                render_report(results, target_col)
                
        except Exception as e:
            st.error(f"An error occurred during file processing or analysis: {e}")
            st.info("Please ensure your CSV is correctly formatted and doesn't contain incompatible data types.")

if __name__ == "__main__":
    main_app()