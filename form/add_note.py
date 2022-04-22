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
    # all_themes = get(config.address + 'api/user_get_themes/273664689').json()['answer']
    # notes = []
    # for i in all_themes:
    #     note = get(config.address + f'api/user_get_notes/{i}').json()['answer']
    #     for j in note:
    #         req = f'/api/get_id_note/{j}/{i}'
    #         id = get(config.address + req).json()['answer']
    #         notes.append((j, id))
    # links = MultiCheckboxField(label='сслыки',
    #                            choices=notes)
    submit = SubmitField('добавить')

    def __init__(self, t, obj, id):
        super().__init__(t, obj)
