import pandas as pd
import sys
import os

# 1. Add the project root to Python's search path to resolve ModuleNotFoundErrors
# This ensures docs/report.py can see src/data_processing/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. STANDARDIZED IMPORTS
from src.data_processing.pre_data import PreData
from src.data_processing.process_data import ProcessData
from src.data_processing.post_data import PostData
from src.utils.git_manager import GitManager
from src.utils.data_versioning import DataVersioning
from security.trash_manager import TrashManager
from docs.report import Report


def main():
    # --- LOAD DATA ---
    # Constructing the absolute path to your dataset in the /data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "data", "Corporate_Financial_Risk_Assessment_Data.csv")

    if not os.path.exists(data_path):
        print(f"❌ [ERROR] Data file not found at: {data_path}")
        print("Please check if the file is inside the 'data' folder and spelled correctly.")
        return

    df = pd.read_csv(data_path)
    print(f"✅ [SUCCESS] Loaded dataset: {data_path}")

    # --- INIT SYSTEMS ---
    git = GitManager()
    versioning = DataVersioning(folder="data_versions")
    trash = TrashManager()

    # --- STEP 1: PRE-ANALYSIS ---
    pre = PreData(df)
    pre_info = pre.basic_info()
    print(f"📊 [INFO] Initial Shape: {pre_info['shape']}")

    # --- STEP 2: PROCESSING ---
    processor = ProcessData(df)
    # Removing ID and Date columns as per standard ML practice
    cols_to_drop = [c for c in ['Company_ID', 'Date'] if c in df.columns]
    df_temp = df.drop(cols_to_drop, axis=1)

    processor = ProcessData(df_temp)
    df_clean = processor.handle_missing()
    df_clean = processor.remove_outliers_iqr()
    df_clean = processor.encode_categorical()
    df_clean = processor.scale_features()

    # Save versions for reproducibility
    versioning.save(df, "raw")
    versioning.save(df_clean, "cleaned")

    # --- STEP 3: POST-ANALYSIS ---
    post = PostData(df_clean)
    post_summary = post.summary()
    correlation = post.correlation()

    # --- STEP 4: REPORTS ---
    # Saving reports to the dedicated output folder
    report = Report(
        df_before=df,
        df_after=df_clean,
        pre_info=pre_info,
        post_summary=post_summary,
        correlation=correlation
    )
    report.save_all(folder="report_outputs")

    # --- STEP 5: HOUSEKEEPING & GIT ---
    trash.safe_delete("old_model_results.csv")
    git.auto_commit(f"EDA pipeline executed. Processed {len(df_clean)} rows.")
    print(" Pipeline complete! Reports generated in /report_outputs")


if __name__ == "__main__":
    main()