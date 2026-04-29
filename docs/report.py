import os
import pandas as pd
import json

try:
    from docs.visual_report import VisualReport
except ImportError:
    from visual_report import VisualReport

class Report:
    def __init__(self, df_before, df_after, pre_info, post_summary, correlation=None):
        self.df_before = df_before
        self.df_after = df_after
        self.pre_info = pre_info
        self.post_summary = post_summary
        self.correlation = correlation

    def save_all(self, folder="report_outputs"):
        # Create full path relative to project root
        os.makedirs(folder, exist_ok=True)

        # Save datasets
        self.df_before.to_csv(f"{folder}/raw_data.csv", index=False)
        self.df_after.to_csv(f"{folder}/cleaned_data.csv", index=False)
        self.post_summary.to_csv(f"{folder}/summary.csv")

        if self.correlation is not None:
            self.correlation.to_csv(f"{folder}/correlation.csv")

        # JSON safe dump
        with open(f"{folder}/pre_info.json", "w", encoding="utf-8") as f:
            json.dump(self.pre_info, f, indent=4, default=str)

        # VISUALS
        visual = VisualReport(self.df_before)
        visual.save_missing_plot(folder)
        visual.save_correlation_heatmap(folder)
        visual.save_histograms(folder)

        print(f" Full report saved in '{folder}'")