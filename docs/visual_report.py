import matplotlib.pyplot as plt
import seaborn as sns
import os

class VisualReport:
    def __init__(self, df):
        self.df = df
        sns.set_theme(style="whitegrid")

    def save_missing_plot(self, folder):
        plt.figure(figsize=(10, 6))
        sns.heatmap(self.df.isnull(), yticklabels=False, cbar=False, cmap='viridis')
        plt.title("Missing Data Map")
        plt.savefig(os.path.join(folder, "missing_data_map.png"))
        plt.close()

    def save_correlation_heatmap(self, folder):
        plt.figure(figsize=(12, 10))
        numeric_df = self.df.select_dtypes(include=['float64', 'int64'])
        sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap='coolwarm')
        plt.title("Feature Correlation Heatmap")
        plt.savefig(os.path.join(folder, "correlation_heatmap.png"))
        plt.close()

    def save_histograms(self, folder):
        self.df.select_dtypes(include=['float64', 'int64']).hist(figsize=(15, 10), bins=20)
        plt.tight_layout()
        plt.savefig(os.path.join(folder, "feature_distributions.png"))
        plt.close()