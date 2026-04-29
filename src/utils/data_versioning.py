import os

class DataVersioning:

    def __init__(self, folder="data_versions"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.version = 1

    def save(self, df, name="data"):
        path = f"{self.folder}/v{self.version}_{name}.csv"
        df.to_csv(path, index=False)   #lazımsız sıra nömrələrinin fayla düşməsinin qarşısını alır
        print(f" Saved: {path}")
        self.version += 1