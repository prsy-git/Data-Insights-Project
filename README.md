# Data Insights

This project is a Flask-based web application for lightweight exploratory analysis of ingested structured datasets. Users can upload CSV, Excel, or JSON files or import datasets from Kaggle, then preview, clean, and visualize their data through a browser-based dashboard.

Additionally, the application provides basic quality checks for missing values and potential outliers, alongside allowing the generation of configurable box and scatter plots for comparing numeric columns of ingested datasets. This application also supports user authentication and storage of Kaggle API credentials for importing authenticated datasets from Kaggle URLs.

## Features

- **Local dataset uploads** — Upload and analyze CSV, Excel and JSON datasets.
- **Kaggle dataset imports** — Import datasets directly from Kaggle using credentials for an existing Kaggle user account.
- **Dataset preview** — Inspect the first 50 rows of the active dataset through a scrollable table to preview the data.
- **Data cleaning** — Remove rows containing missing values from columns selected by the user.
- **Data quality checks** — Identify columns with significant (> 10%) amounts of missing data and flag numeric outliers calculated with the IQR formula.
- **Data visualization** — Compare numeric variables using box plots and scatter plots.
- **User authentication** — Register and log into accounts with hashed and salted passwords stored in an SQLite database.
- **Credential protection** — Store Kaggle API credentials using Fernet symmetric encryption when passing to functions for use.

## Tech Stack

- **Backend:** Python, Flask
- **Data Processing:** Pandas
- **Visualization:** Matplotlib, Seaborn
- **Database:** SQLite
- **Authentication and Security:** PBKDF2-HMAC, Fernet encryption
- **Frontend:** HTML, CSS, Jinja2, Bootstrap
- **External API:** Kaggle API

## Getting Started / Running the Application

## Prerequsites

- Python 3.10 or later
- `pip`
- A Kaggle account and API credentials

### Installation

1. Clone repository and enter project directory at:

    ```
    git clone https://github.com/prsy-git/Data-Insights-Project
    cd Data-Insights-Project
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate virtual environment:

    **Windows (PowerShell):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bash
   python app.py
   ```

6. Open the local address displayed by Flask in a browser (typically and by default `http://127.0.0.1:5000`).

7. Optionally, create a .env file in the form of .env.example with Kaggle credentials to use Kaggle features.

## Usage

1. Open the Data Dashboard.
2. Upload a CSV, Excel or JSON dataset, or import a public dataset from Kaggle.
3. Preview the first 50 rows and review the automatically generated quality warnings at the bottom of the page.
4. Select columns to remove for missing values if you would like to do so at this time.
5. Select two numeric columns and a supported chart type to generate a bivariate analysis graph of selected variables.

Kaggle imports require that an account have an associated Kaggle username and API token. Local dataset uploads can be used without an attached Kaggle account.

## Limitations

- This application is intended for quick and lightweight data analysis rather than comprehensive or dataset-specific results. By allowing ingestion of any files, specific large-scale data processing operations were not feasible to integrate.
- Visualizations rely on user input and discretion for selecting appropriate variables and chart types to generate a visual. Unsuitable selections may generate unclear or malformed visuals.
- Data quality checks are limited to numeric outliers implemented with the IQR method and a percentage-based missing value threshold.
- User accounts and application data are stored locally with SQLite and not intended for production use or implementation.
- Kaggle imports take the first found CSV, Excel or JSON file in a downloaded dataset that is supported by the application.


