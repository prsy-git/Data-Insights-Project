import pandas as pd
import numpy as np

def load_dataframe(file_path:str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

def count_rows(df:pd.DataFrame) -> int:
    return len(df)

def count_columns(df:pd.DataFrame) -> int:
    col = df.columns
    return len(col)
