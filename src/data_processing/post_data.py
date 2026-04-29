import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier


# ... (Keep your PreData and ProcessData classes here) ...

class PostData:
    """Class for Post-Processing Analysis and Feature Evaluation."""

    def __init__(self, df):
        self.df = df

    def summary(self):
        return self.df.describe()

    def correlation(self):
        # Ensure only numeric data is used for correlation
        return self.df.corr(numeric_only=True)

    def feature_importance(self, target='Financial_Risk_Label'):
        """Identifies which features are most predictive of risk."""
        X = self.df.drop(columns=[target])
        y = self.df[target]

        # Using a fast Random Forest to rank features
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        importance = pd.Series(model.feature_importances_, index=X.columns)
        return importance.sort_values(ascending=False)


def run_full_pipeline(file_name):
    # 1. Load and Clean
    # (Using the dynamic path logic from previous steps)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../"))
    data_path = os.path.join(project_root, 'data', file_name)

    df_raw = pd.read_csv(data_path).drop(['Company_ID', 'Date'], axis=1)

    # 2. Process
    processor = ProcessData(df_raw)
    processor.handle_missing()
    processor.encode_categorical()
    df_processed = processor.scale_features()

    # 3. Evaluate Features (PostData)
    evaluator = PostData(df_processed)
    print("\n--- Top 5 Most Important Features for Risk Prediction ---")
    print(evaluator.feature_importance().head(5))

    return df_processed