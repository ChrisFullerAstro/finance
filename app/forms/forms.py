from flask_wtf import Form, FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, BooleanField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class ConfigForm(FlaskForm):
    SIMILARITY_THRESHOLD = StringField('Similary Threshold for Automatic Acceptance', validators=[DataRequired()], default='0.7')

class UploadForm(FlaskForm):
    file_name = FileField('Data File')
    dtype =  SelectField('Data Type', choices=[('barclays','Barclays'), ('barclaycard','Barclaycard'), ('config','Historical Data')])

class ClassficationForm(FlaskForm):
    ctype =  SelectField('Category Type', choices=[])
