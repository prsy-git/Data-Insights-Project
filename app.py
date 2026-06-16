import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import analytics

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-dev-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#webapp page routes

@app.route('/')
def home():
    return render_template('index.html')

#file upload handling and routes
def is_allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    #Validation logic for file passing
    if request.method != 'POST':
        return render_template('dashboard.html')
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        flash('No seelcted file')
        return redirect(request.url)
    
    if not is_allowed_file(file.filename):
        flash('File type not allowed')
        return redirect(request.url)
    
    filename = secure_filename(file.filename)
    file_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_dest)

    #Trigger the analytics calls on POST routing.
    dashboard_df = analytics.load_dataframe(file_dest)
    dashboard_data = analytics.create_dashboard_data(dashboard_df)

    return render_template('dashboard.html', data=dashboard_data)
    
    



if __name__ == '__main__':
    app.run(debug=True)

