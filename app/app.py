import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from models import data_manager, category_selector

UPLOAD_FOLDER = '/Users/chrisfuller/Dropbox/Programs/finance_v2/finance/data/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

dm = data_manager.DataManager()
cs = category_selector.Category_Selector(dm)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
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
            dm.load_input_data(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            transactions_with_suggestions = [cs.suggest_category(x)[1] for x in dm.input_data]
            return render_template('data_viz.html', data=transactions_with_suggestions)


            #return redirect(url_for('uploaded_file',filename=filename))
    return '''
    <!doctype html>
    <title>Welcome</title>
    <h1>Please Upload File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
app.run(debug=True)
