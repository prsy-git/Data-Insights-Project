import os
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import zipfile

#load environment variables before use in analytics
load_dotenv()
import analytics

print("ENV DEBUG CHECK")
print("Username: ", os.environ.get("KAGGLE_USERNAME"))
print("KEY: ", os.environ.get("KAGGLE_API_TOKEN"))

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-dev-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['PROCESSED_FILE_NAME'] = 'active_data.csv'

#webapp page routes

@app.route('/')
def home():
    return render_template('index.html')

#Dashboard routes
def is_allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    #Validation logic for file passing
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '' and is_allowed_file(file.filename):
                _, file_extension = os.path.splitext(file.filename)
                filename = f"active_data{file_extension}"
                file_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_dest)
    
    #read in case of no file
    active_file = None
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file.startswith("active_data"):
                active_file = file
                break

    #otherwise if active file
    if active_file:
        file_dest = os.path.join(app.config['UPLOAD_FOLDER'], active_file)
        dashboard_df = analytics.load_dataframe(file_dest)
        dashboard_data = analytics.create_dashboard_data(dashboard_df)
        return render_template('dashboard.html', data=dashboard_data)
    
    return render_template('dashboard.html')

@app.route('/dashboard/kaggle-import', methods=['POST'])
def kaggle_import():
    kaggle_url = request.form.get('url')

    if not kaggle_url:
        flash("Invalid kaggle URL. Please try again.")
        return redirect(url_for('dashboard'))
    
    try:
        extracted_path = analytics.download_kaggle_dataset(kaggle_url, UPLOAD_FOLDER)

        _, file_extension = os.path.splitext(extracted_path)

        filename = f"active_data{file_extension}"
        active_destination = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.exists(active_destination):
            os.remove(active_destination)
        os.rename(extracted_path, active_destination)

        dashboard_df = analytics.load_dataframe(active_destination)
        dashboard_data = analytics.create_dashboard_data(dashboard_df)

        return render_template('dashboard.html', data=dashboard_data)

    except Exception as error:
        flash("Error: Failed kaggle import. Please try again")
        return redirect(url_for('dashboard'))

@app.route('/dashboard/clean_values', methods=['POST'])
def clean_data():
    active_file = None
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.startswith("active_data"):
            active_file = file
            break

    if not active_file:
        flash("No active file")
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], active_file)

    df = analytics.load_dataframe(file_path)
    clean_df = analytics.button_drop_missing(df)

    #Reconstruct file with removed data
    if file_path.endswith('.csv'):
        clean_df.to_csv(file_path, index=False)
    elif file_path.endswith('.xlsx'):
        clean_df.to_excel(file_path, index=False)
    elif file_path.endswith('.json', orient='records'):
        clean_df.to_json(file_path)

    flash("Cleaned data. Empty cells dropped.")

    dashboard_data = analytics.create_dashboard_data(clean_df)
    return render_template('dashboard.html', data=dashboard_data)

@app.route('/dashboard/plot', methods=['POST'])
def plot_bivariate():
    
    #Write helper function to duplicate this code later
    active_file = None
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.startswith("active_data"):
            active_file = file
            break

    if not active_file:
        flash("No active file")
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], active_file)
    df = analytics.load_dataframe(file_path)
    #Write helper function to duplicate this code later
    
    x_col_name = request.form.get('column_a')
    y_col_name = request.form.get('column_b')

    x_series = df[x_col_name]
    y_series = df[y_col_name]

    #Code to clear previous graphs if existing
    plt.clf()
    graph_axes = analytics.graph_comparison(x_series, y_series)

    plot_filename = "dashboard_plot.png"
    plot_filepath = os.path.join(app.root_path, 'static', 'images', plot_filename)

    os.makedirs(os.path.dirname(plot_filepath), exist_ok=True)

    plt.savefig(plot_filepath, bbox_inches='tight')

    #Timestamp to reset current graphs
    timestamp = int(time.time())

    dashboard_data = analytics.create_dashboard_data(df)
    return render_template('dashboard.html', data=dashboard_data, graph=plot_filename, timestamp = timestamp)

if __name__ == '__main__':
    app.run(debug=True)

