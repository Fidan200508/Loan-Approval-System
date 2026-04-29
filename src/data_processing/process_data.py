import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder


class ProcessData:
    def __init__(self, df):
        self.df = df.copy()

    def handle_missing(self):
        for col in self.df.columns:
            if self.df[col].dtype in ['int64', 'float64']:
                # Using median for financial data is often safer than mean
                # because it's less sensitive to extreme outliers.
                self.df[col] = self.df[col].fillna(self.df[col].median())
            else:
                self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
        return self.df

    def remove_outliers_iqr(self):
        df = self.df.copy()
        for col in df.select_dtypes(include=np.number).columns:
            # Skip the target label - we don't want to remove 'High Risk' cases!
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
        # Scale everything except the target label
        features = self.df.drop('Financial_Risk_Label', axis=1)
        num_cols = features.select_dtypes(include=np.number).columns
        self.df[num_cols] = scaler.fit_transform(self.df[num_cols])
        return self.df


# --- This is the function the AI Team will call ---
def run_full_processing(file_name):
    # Dynamic path logic from our previous step
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_path, 'data', file_name)

    df = pd.read_csv(path).drop(['Company_ID', 'Date'], axis=1)

    # Initialize your class
    processor = ProcessData(df)

    # Execute pipeline
    processor.handle_missing()
    processor.remove_outliers_iqr()
    processor.encode_categorical()
    df_final = processor.scale_features()

    print(f"Data processed. Final shape: {df_final.shape}")
    return df_final


if __name__ == "__main__":
    run_full_processing('Corporate_Financial_Risk_Assessment_Data.csv')