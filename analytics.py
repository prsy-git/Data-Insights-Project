import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile

def load_dataframe(file_path:str) -> pd.DataFrame:
    #conditional logic for each possible file extension, currently: xlsx, csv, json
    extension_str = file_path.split('.', 1)[1]
    
    if extension_str == "csv":
        df = pd.read_csv(file_path)

    elif extension_str == "xlsx":
        df = pd.read_excel(file_path)

    elif extension_str == "json":
        df = pd.read_json(file_path)
    
    
    return df

def count_rows(df:pd.DataFrame) -> int:
    return len(df)

def count_columns(df:pd.DataFrame) -> int:
    col = df.columns
    return len(col)

def button_drop_missing(df:pd.DataFrame) -> None:
    cleaned_df = df.dropna()
    return cleaned_df

def download_kaggle_dataset(url: str, dest_folder: str) -> str:
    api = KaggleApi()
    api.authenticate()

    #Split url into function readable handle string
    handle = url.split("kaggle.com/datasets/")[1].split("?")[0]

    api.dataset_download_files(handle, path=dest_folder, unzip=True)

    #find extracted file of interest
    for file in os.listdir(dest_folder):
        if file.endswith((".csv", ".xlsx", ".json")):
            path = os.path.join(dest_folder, file)
            return path
        
    raise FileNotFoundError("File not found in KaggleAPI Pull")

def get_numeric_columns(df: pd.DataFrame) -> list:
    column_list = df.columns.to_list()
    numeric_cols = []

    for col in column_list:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)

    return numeric_cols

#Returns a matplot axes value
def graph_comparison(col1: pd.Series, col2: pd.Series):
    x_series = col1
    y_series = col2

    plt.figure(figsize=(8, 5))

    axes_plot = sns.scatterplot(x = x_series, y = y_series, alpha=0.6)
    axes_plot.set_title("Bivariate Analysis of Selected Numeric Variables from Dataset")
    plt.tight_layout()

    return axes_plot

def create_dashboard_data(passed_df:pd.DataFrame) -> dict:

    analysis_dict = {
        "row_count": count_rows(passed_df),
        "col_count": count_columns(passed_df),
        "html_table": passed_df.head(50).to_html(),
        "col_list": passed_df.columns.tolist(),
        "numeric_col_list": get_numeric_columns(passed_df)
    }

    return analysis_dict

