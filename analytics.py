import pandas as pd

def count_rows(file_path:str) -> int:
    df = pd.read_csv(file_path)

    row_count = len(df)

    return row_count
