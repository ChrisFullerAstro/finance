import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from models import data_manager, category_selector
from forms import forms

UPLOAD_FOLDER = '/Users/chrisfuller/Dropbox/Programs/finance_v2/finance/data/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'

dm = data_manager.DataManager()
cs = category_selector.Category_Selector(dm)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    # if request.method =='POST':
    #     if 'upload' in request.form.values():
    #         return redirect(url_for('upload_file'))
    #
    #     if 'config' in request.form.values():
    #         return redirect(url_for('configuration_cs'))

    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    return render_template('login.html',
                           form=form)


@app.route('/configuration_cs', methods=['GET', 'POST'])
def configuration_cs():
    cs_config_data = cs.get_config()
    form = forms.ConfigForm()

    return render_template('config.html', form=form, **cs_config_data)

# @app.route('/configuration_cs', methods=['GET', 'POST'])
# def configuration_cs():
#     if request.method =='POST':
#
#         return render_template('config_cs.html', **cs.get_config())
#
#     cs_config_data = cs.get_config()
#
#     return render_template('config_cs.html', **cs_config_data)


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('processtransactions',filename=filename))

    return render_template('upload.html')

@app.route('/processtransactions/<filename>', methods=['GET', 'POST'])
def processtransactions(filename):
    if request.method == 'POST':
            # ddm.save_transactions_bulk(
            return redirect(url_for('users_input_required'))

    dm.load_input_data(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    automatic_classfied, users_input_required = cs.suggest_categoies_bulk(dm.input_data)

    return render_template('data_viz.html', auto_data=automatic_classfied, nauto_data=users_input_required)

@app.route('/current_transactions')
def current_transactions():
    return render_template('render_data.html', data=dm.load_current_transactions())

@app.route('/users_input_required', methods=['GET', 'POST'])
def users_input_required():
    if request.method == 'POST':
        # check if the post request has the file part
        return 'POST'
    return 'Users Input Required'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

app.run(debug=True)
