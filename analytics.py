import os
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
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

def button_drop_missing(df:pd.DataFrame, target_columns: list = None) -> None:
    if target_columns:
        #Drop if columns to be checked for missing values are selected by user
        cleaned_df = df.dropna(subset=target_columns)
    else:
        #Otherwise, drop for all columns
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

def dataset_quality_alerts(df):
    result = {
        "warnings": [],
        "confirmed_clear": "",
        "outlier_details": {}
    }

    #If a specific column has a large amount of missing values (> 10%), throw an alert
    missing_counts = df.isnull().sum()
    ten_percent_missing = missing_counts[missing_counts > (len(df) * 0.1)]
    
    if not ten_percent_missing.empty:
        cols = ", ".join(ten_percent_missing.index)
        counts_warning = f"Alert: The columns {cols} are missing greater than 10% of their values. Cleaning the dataset with clean data button or external analysis is recommended."
        result["warnings"].append(counts_warning)

    #If ANY column contains outliers based on its quantile values, alert here. Have a separate dropdown in which specific values for specific columns can be viewed.
    numeric_cols = get_numeric_columns(df)
    affected_columns = []

    for col in numeric_cols:
        first_quantile = df[col].quantile(0.25)
        third_quantile = df[col].quantile(0.75)
        innerquartile_range = third_quantile - first_quantile

        outliers = df[(df[col] < (first_quantile - 1.5 * innerquartile_range)) | (df[col] > (third_quantile + 1.5 * innerquartile_range))]
        
        if len(outliers) > 0:
            affected_columns.append(col)
            #Put column name and number of data points affected as a tuple entry in dictionary
            result["outlier_details"][col] = len(outliers)

    if affected_columns:
        cols_str = ", ".join(affected_columns)
        result["warnings"].append(f"🔍 Outliers detected in: [{cols_str}]. Open the dropdown below to review.")

    if not result["warnings"]:
        result["confirmed_clear"] = f"Dataset confirmed to not have any significant issues. There still may be some missing values, so clean if necessary"

    return result

#Returns a matplot axes value
def graph_comparison(col1: pd.Series, col2: pd.Series, graph_type: str):
    #TODO: add cases allowing users to select multiple types of graphs, read in from form dropdown
    x_series = col1
    y_series = col2

    plt.figure(figsize=(8, 5))
    axes_plot = None
    
    match graph_type:
        case "box":
            axes_plot = sns.boxplot(x = x_series, y = y_series)
        case "scatter":
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
        "numeric_col_list": get_numeric_columns(passed_df),
        "quality_report": dataset_quality_alerts(passed_df)
    }

    return analysis_dict

