import os
import csv
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, session, flash
from werkzeug.utils import secure_filename
# from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo
from models import category_selector, loaders
from forms import forms
import logging
import datetime
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__)
app.config.from_pyfile('config.py')
db_finance = PyMongo(app)
db_config = PyMongo(app, config_prefix='MONGO2')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    #get config data
    session['config_data'] = category_selector.get_config(db_config.db.cs_config)
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method == 'POST' and form.validate():
        flash('Welcome back {0}, you have logged in successfully'.format(form.username.data), 'success')
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title='login')


@app.route('/configuration_cs', methods=['GET', 'POST'])
def configuration_cs():
    updated = ''
    form = forms.ConfigForm()
    if request.method == 'POST' and form.validate():
        category_selector.update_config(db_config.db.cs_config,{
                    "THRESHOLD_ACCEPT_DISTANCE": float(form.TA_distance.data),
                    "THRESHOLD_ACCEPT_LIKELYHOOD_EM":float(form.TA_likelyhood_em.data),
                    "THRESHOLD_ACCEPT_LIKELYHOOD_LD":float(form.TA_likelyhood_ld.data)
                        })
        session['config_data'] = category_selector.get_config(db_config.db.cs_config)
        flash('Configuration updated successfully', 'success')

    config_data = session.get('config_data', category_selector.get_config(db_config.db.cs_config))
    form.TA_distance.data = str(config_data['THRESHOLD_ACCEPT_DISTANCE'])
    form.TA_likelyhood_em.data = str(config_data['THRESHOLD_ACCEPT_LIKELYHOOD_EM'])
    form.TA_likelyhood_ld.data = str(config_data['THRESHOLD_ACCEPT_LIKELYHOOD_LD'])
    return render_template('config.html', form=form, title='Configuration')

@app.route('/current_transactions', methods=['GET', 'POST'])
def current_transactions():
    if request.method == "POST":
        if request.form.get('button', None) == 'clear':
            logging.info('clear transactions')
            session['current_transactions'] = []
            flash('Transactions cleared', 'success')
            return redirect(url_for('home'))

        if request.form.get('button', None) == 'commit':
            logging.info('commited transactions')
            fieldnames = ["date","account","ammount","description","payee","category"]
            transactions_filtered = loaders.filter_dicts(session['current_transactions'], fieldnames)
            for transaction in transactions_filtered:
                try:
                    db_finance.db.processedtransactions.insert_one(transaction)
                except:
                    flash('One transaction could not be commited as it was a duplicate', 'danger')
            flash('Transactions commited to database', 'success')
            return redirect(url_for('current_transactions'))

        if request.form.get('button', None) == 'export':
            logging.info('export transactions')
            fname ='output_'+ str(datetime.date.today()) +'.csv'
            with open(os.path.join(app.config['UPLOAD_FOLDER'], fname), 'w') as csvfile:
                fieldnames = ["date","account","ammount","description","payee","category"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(loaders.filter_dicts(session['current_transactions'], fieldnames))

            return redirect(url_for('uploaded_file', filename=fname))
            flash('File saved successfully', 'success')
            return redirect(url_for('current_transactions'))


    data = session.get('current_transactions',None)
    if data:
        return render_template('render_data.html', data=data)
    else:
        flash('You have no current stored transactions', 'danger')
        return redirect(url_for('home'))



@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    form = forms.UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file_name.data.filename)
        form.file_name.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('processtransactions',filename=filename))
    else:
        filename = None
    return render_template('upload.html', form=form)


@app.route('/processtransactions/<filename>', methods=['GET', 'POST'])
def processtransactions(filename):
    if request.method == 'POST':
            if session['users_input_required'] != [] and session['automatic_classfied'] != []:
                session['current_transactions'] = session['automatic_classfied']
                flash('Automatically Classfied {0} transactions'.format(len(session['automatic_classfied'])),'success')
                return redirect(url_for('users_input_required'))

            elif session['users_input_required'] != [] and session['automatic_classfied'] == []:
                flash('No transactions could be automatic classfied {0} need human classfication'.format(len(session['users_input_required'])), 'info')
                return redirect(url_for('current_transactions'))

            elif session['users_input_required'] == [] and session['automatic_classfied'] != []:
                session['current_transactions'] = session['automatic_classfied']
                flash('Automatically Classfied {0} transactions, No transactions need human classfication'.format(len(session['automatic_classfied'])), 'success')
                return redirect(url_for('current_transactions'))

            else:
                flash('No transactions found make sure the file is not empty', 'danger')
                return redirect(url_for('home'))

    session['classfied']=[]
    session['automatic_classfied'] = []
    session['users_input_required'] = []

    session['input_data'] = loaders.load_data(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cs_config = session.get('config_data', category_selector.get_config(db_config.db.cs_config))
    automatic_classfied, users_input_required = category_selector.suggest_categoies_bulk(session['input_data'], cs_config, db_finance.db.master)

    session['automatic_classfied'] = automatic_classfied
    session['users_input_required']= users_input_required

    return render_template('data_viz.html', data=automatic_classfied)

@app.route('/users_input_required', methods=['GET', 'POST'])
def users_input_required():
    form = forms.ClassficationForm()
    if request.method == 'POST':
        # check if the post request has the file part
        ct = session.get('current_transaction')
        ct.update({'category':form.ctype.data})
        session['classfied'].append(ct)

    if len(session['users_input_required']) == 0:
        current_transaction = None
    else:
        current_transaction = session['users_input_required'].pop(0)

    session['current_transaction'] = current_transaction

    if current_transaction:
        form.ctype.choices=[]
        # for cat in ['House + Groceries', 'Other + Other', 'Leisure + Entertainment', 'House + Groceries']:
        for cat in current_transaction['suggestions']:
            form.ctype.choices.append((cat, cat))

        return render_template('user_classfier.html',
            form=form,
            t=current_transaction,
            awaing_classfication=session['users_input_required'],
            already_classfied=session.get('classfied'))
    else:
        session['current_transactions'].extend(session.get('classfied',[]))
        flash('Weldone! Human classfication Complete! You classfied {0} transactions manually'.format(len(session.get('classfied', []))), 'success')
        return redirect(url_for('current_transactions'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
     return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

app.run(host='0.0.0.0')
