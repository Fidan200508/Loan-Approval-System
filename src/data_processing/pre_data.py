import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder


class PreData:
    """Class for Exploratory Data Analysis (EDA) and Reporting."""

    def __init__(self, df):
        self.df = df

    def basic_info(self):
        return {
            "shape": self.df.shape,
            "columns": self.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }

    def missing_report(self):
        missing = self.df.isnull().sum()
        percent = (missing / len(self.df)) * 100
        return pd.DataFrame({"Missing": missing, "Percent": percent})

    def correlation(self):
        return self.df.corr(numeric_only=True)


class ProcessData:
    """Class for Data Cleaning and Feature Engineering."""

    def __init__(self, df):
        self.df = df.copy()

    def handle_missing(self):
        for col in self.df.columns:
            if self.df[col].dtype in ['int64', 'float64']:
                self.df[col] = self.df[col].fillna(self.df[col].median())
            else:
                self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
        return self.df

    def remove_outliers_iqr(self):
        df = self.df.copy()
        for col in df.select_dtypes(include=np.number).columns:
            if col == 'Financial_Risk_Label': continue
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]
        self.df = df
        return self.df

    def encode_categorical(self):
        le = LabelEncoder()
        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = le.fit_transform(self.df[col])
        return self.df

    def scale_features(self):
        scaler = StandardScaler()
        # Ensure we don't scale the target label
        target = 'Financial_Risk_Label'
        if target in self.df.columns:
            features = self.df.drop(target, axis=1)
            num_cols = features.select_dtypes(include=np.number).columns
            self.df[num_cols] = scaler.fit_transform(self.df[num_cols])
        return self.df


def run_full_pipeline(file_name):
    """Main function to execute the full data lifecycle."""
    # 1. Dynamic Path Resolution
    # Adjusting for nested 'Loan-Approval-System/Loan-Approval-System' structure
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../"))
    data_path = os.path.join(project_root, 'data', file_name)

    print(f"Loading data from: {data_path}")
    df_raw = pd.read_csv(data_path)

    # 2. Analyze
    analyzer = PreData(df_raw)
    print("\n[INFO] Initial Shape:", analyzer.basic_info()['shape'])
    print("\n[INFO] Missing Data Report:\n", analyzer.missing_report().head())

    # 3. Process
    # Drop identifiers before ML logic
    df_clean = df_raw.drop(['Company_ID', 'Date'], axis=1)

    processor = ProcessData(df_clean)
    processor.handle_missing()
    processor.remove_outliers_iqr()
    processor.encode_categorical()
    df_final = processor.scale_features()

    print("\n[SUCCESS] Final processed shape:", df_final.shape)
    return df_final


if __name__ == "__main__":
    final_data = run_full_pipeline('Corporate_Financial_Risk_Assessment_Data.csv')