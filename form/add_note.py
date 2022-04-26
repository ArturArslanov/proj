from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, IntegerField, \
    StringField, SelectField, RadioField, SelectMultipleField, FieldList, HiddenField, widgets
from wtforms.validators import DataRequired

from config import bd_path
from data import db_session
from data.User import User
from requests import get
import config


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddNoteForm(FlaskForm):
    header = StringField('название заметки', validators=[DataRequired()])
    text = StringField('текст заметки', validators=[DataRequired()])
    links = StringField('ссылки разделёные "/"')
    submit = SubmitField('добавить')

