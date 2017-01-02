from flask_wtf import Form
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class ConfigForm(Form):
        TA_likelyhood_ld = StringField('Acceptance Threshold likelyhood: Levenshtein Distance', validators=[DataRequired()], default='7')
        TA_likelyhood_em = StringField('Acceptance Threshold likelyhood: Exact Match', validators=[DataRequired()], default='0.7')
        TA_distance = StringField('Acceptance Threshold Levenshtein Distance', validators=[DataRequired()], default='0.7')
