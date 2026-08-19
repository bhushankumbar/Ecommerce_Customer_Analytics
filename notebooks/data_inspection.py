import pandas as pd
from pathlib import Path

data_path = Path("data/raw")

for file in data_path.glob("*.csv"):
    df = pd.read_csv(file)

    print(f"\n{'=' * 60}")
    print(f"FILE: {file.name}")
    print(f"SHAPE: {df.shape}")
    print(f"COLUMNS: {list(df.columns)}")
    print(f"NULL VALUES:\n{df.isnull().sum()}")