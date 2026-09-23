import os
import shutil
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from flask import Flask, render_template, flash, request, redirect, url_for, session
from db_helper import init_auth_db, register_user, verify_user, get_encrypted_user_api, MASTER_KEY

load_dotenv()
import analytics

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

app = Flask(__name__)
app.config['SECRET_KEY'] = MASTER_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)

init_auth_db()

@app.route('/')
def home():
    return render_template('index.html')

def is_allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_active_file() -> str | None:
    upload_folder = app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_folder):
        return None

    for filename in os.listdir(upload_folder):
        if filename.startswith("active_data"):
            return filename

    return None

def clear_active_files() -> None:
    upload_folder = app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_folder):
        return

    for filename in os.listdir(upload_folder):
        if filename.startswith("active_data"):
            os.remove(os.path.join(upload_folder, filename))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    '''
    Handle the dashboard page routing, allowing users to upload files and view the dashboard.
    '''
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '' and is_allowed_file(file.filename):
                _, file_extension = os.path.splitext(file.filename)
                filename = f"active_data{file_extension}"
                file_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_dest)

                flash("Local file uploaded.")
                return redirect(url_for('dashboard'))
    
    active_file = get_active_file()

    if active_file:
        file_dest = os.path.join(app.config['UPLOAD_FOLDER'], active_file)
        dashboard_df = analytics.load_dataframe(file_dest)
        dashboard_data = analytics.create_dashboard_data(dashboard_df)
        return render_template('dashboard.html', data=dashboard_data)
    
    return render_template('dashboard.html')

@app.route('/dashboard/kaggle-import', methods=['POST'])
def kaggle_import():
    #Ensure Kaggle credentials are available before attemtping an import
    if 'user_id' not in session:
        flash("Log in to an account with a kaggle account associated first to access the dataset import feature.")
        return redirect(url_for('login_page'))
    
    check_user_id = session.get('user_id')
    kaggle_user, kaggle_key = get_encrypted_user_api(check_user_id)

    if not kaggle_user or not kaggle_key:
        flash("An existing kaggle username and api key must be associated with this account to access this feature. Please add those to your account.")
        return redirect(url_for('login_page'))

    os.environ["KAGGLE_USERNAME"] = kaggle_user
    os.environ["KAGGLE_API_TOKEN"] = kaggle_key

    kaggle_url = request.form.get('url')

    if not kaggle_url:
        flash("Invalid kaggle URL. Please try again.")
        return redirect(url_for('dashboard'))
    
    try:
        #Clean previous data displayed as active_data if it exists
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for file in os.listdir(app.config['UPLOAD_FOLDER']):
                if file.startswith("active_data"):
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
                    except OSError:
                        pass

        extracted_path = analytics.download_kaggle_dataset(kaggle_url, UPLOAD_FOLDER)
        _, file_extension = os.path.splitext(extracted_path)

        filename = f"active_data{file_extension}"
        active_destination = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.abspath(extracted_path) != os.path.abspath(active_destination):
            shutil.move(extracted_path, active_destination)

        flash("Kaggle file imported successfully.")
        return redirect(url_for('dashboard'))

    except Exception as error:
        print(f"KAGGLE IMPORT ERROR: {error}")
        flash("Error: Failed kaggle import. Please try again")
        return redirect(url_for('dashboard'))

@app.route('/dashboard/clean_values', methods=['POST'])
def clean_data():
    active_file = get_active_file()

    if not active_file:
        flash("No active file")
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], active_file)

    selected_columns = request.form.getlist('columns')

    if not selected_columns:
        flash("Select at least one column from dropdown list to clean column(s).")
        return redirect(url_for('dashboard'))
    
    df = analytics.load_dataframe(file_path)
    clean_df = analytics.button_drop_missing(df, target_columns=selected_columns)

    if file_path.endswith('.csv'):
        clean_df.to_csv(file_path, index=False)
    elif file_path.endswith('.xlsx'):
        clean_df.to_excel(file_path, index=False)
    elif file_path.endswith('.json'):
        clean_df.to_json(file_path, orient='records')

    flash("Cleaned data. Empty cells dropped.")

    dashboard_data = analytics.create_dashboard_data(clean_df)
    return render_template('dashboard.html', data=dashboard_data)

@app.route('/dashboard/plot', methods=['POST'])
def plot_bivariate():
    
    active_file = get_active_file()

    if not active_file:
        flash("No active file")
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], active_file)
    df = analytics.load_dataframe(file_path)

    graph_type = request.form.get('graph_type')

    if not graph_type:
        return "Select a graph type", 400
    
    x_col_name = request.form.get('column_a')
    y_col_name = request.form.get('column_b')

    if not x_col_name or not y_col_name:
        flash("Select both columns to plot.")
        return redirect(url_for('dashboard'))

    x_series = df[x_col_name]
    y_series = df[y_col_name]

    #Clear previous graph if existing
    plt.clf()
    analytics.graph_comparison(x_series, y_series, graph_type)

    plot_filename = "dashboard_plot.png"
    plot_filepath = os.path.join(app.root_path, 'static', 'images', plot_filename)

    os.makedirs(os.path.dirname(plot_filepath), exist_ok=True)

    plt.savefig(plot_filepath, bbox_inches='tight')

    #Cache busting for the plot image to ensure the latest version is displayed
    timestamp = int(time.time())

    dashboard_data = analytics.create_dashboard_data(df)
    return render_template('dashboard.html', data=dashboard_data, graph=plot_filename, timestamp = timestamp)

@app.route('/register', methods = ['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        kaggle_username = request.form.get('kaggle_username')
        api_key = request.form.get('api_key')

        success = register_user(username, password, kaggle_username, api_key)

        if success:
            flash("Account created successfully. You can now log in.")
            return redirect(url_for('login_page'))

        flash("That username is already registered. Please choose another.")
        return redirect(url_for('register_page'))
        
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_id = verify_user(username, password)

        if user_id:
            clear_active_files()

            session['user_id'] = user_id
            session['username'] = username

            flash(f"{username} logged in.")
            return redirect(url_for('dashboard'))
        
        else:
            flash("Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    clear_active_files()
    session.clear()
    flash("You have been logged out of user account.")
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)

