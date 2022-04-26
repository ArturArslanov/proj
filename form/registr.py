from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField, \
    BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    number = StringField('номер телефона', validators=[DataRequired()])
    password = PasswordField('пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня', validators=[DataRequired()])
    submit = SubmitField('Войти')
