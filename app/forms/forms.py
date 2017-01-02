from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class ConfigForm(Form):
        TA_likelyhood_ld = StringField('Acceptance Threshold likelyhood: Levenshtein Distance', validators=[DataRequired()])
        TA_likelyhood_em = StringField('Acceptance Threshold likelyhood: Exact Match', validators=[DataRequired()])
        TA_distance = StringField('Acceptance Threshold Levenshtein Distance', validators=[DataRequired()])
