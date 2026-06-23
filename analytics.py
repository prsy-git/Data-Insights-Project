import os
import pandas as pd
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

def create_dashboard_data(passed_df:pd.DataFrame) -> dict:
    
    analysis_dict = {
        "row_count": count_rows(passed_df),
        "col_count": count_columns(passed_df),
        "html_table": passed_df.head(50).to_html()
    }

    return analysis_dict

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

