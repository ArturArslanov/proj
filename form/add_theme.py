from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField, \
    BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class AddThemeForm(FlaskForm):
    header = StringField('название темы', validators=[DataRequired()])
    user_id = IntegerField('id')
    submit = SubmitField('создать')
