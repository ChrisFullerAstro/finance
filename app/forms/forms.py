from flask_wtf import Form, FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, BooleanField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class ConfigForm(FlaskForm):
    TA_likelyhood_ld = StringField('Acceptance Threshold likelyhood: Levenshtein Distance', validators=[DataRequired()], default='7')
    TA_likelyhood_em = StringField('Acceptance Threshold likelyhood: Exact Match', validators=[DataRequired()], default='0.7')
    TA_distance = StringField('Acceptance Threshold Levenshtein Distance', validators=[DataRequired()], default='0.7')

class UploadForm(FlaskForm):
    file_name = FileField('Data File')
    dtype =  SelectField('Data Type', choices=[('barclays','Barclays'), ('barclaycard','Barclaycard')])

class ClassficationForm(FlaskForm):
    ctype =  SelectField('Category Type', choices=[])
    
