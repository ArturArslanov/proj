from flask_login import login_user
from werkzeug.utils import redirect

import config
import flask
from flask import jsonify, request, render_template
from requests import post

from data import db_session
from data.Theme import Theme
from data.User import User
from form.login import LoginForm
from form.registr import RegisterForm

blueprint = flask.Blueprint(
    'api_jobs',
    __name__,
    template_folder='../templates'
)


@blueprint.route('/api/user_nomer/<int:id>/<string:nomer>', methods=['GET'])
def check_user_nomer(id, nomer):
    user = User.user_from_id(id)
    answer = user.check_nomer(nomer)
    return jsonify(
        {
            'answer': answer
        }
    )


@blueprint.route('/api/user_add/', methods=['POST'])
def add_user():
    req = request.json
    name = req['name']
    nomer = req['nomer']
    session = db_session.create_session()
    user = session.query(User).filter(User.hashed_nomer == config.hashing(nomer)).first()
    answer = User.add_user(name, nomer)
    id = req['tele_id']
    if user:
        themes = user.all_themes()
        for theme_id in themes:
            theme = session.query(Theme).filter(Theme.id == theme_id).first()
            theme.user_id = id
    User.set_id(nomer, id)
    Theme.add_theme(header='всякое', user_id=id)
    if user and user.password:
        session.commit()
        session.close()
        return jsonify({
            'answer': answer
        })
    session.close()
    return jsonify({'answer': 'регистрация'})


@blueprint.route('/api/add_password/', methods=['POST'])
def add_password():
    req = request.json
    id = req['user_id']
    password = req['password']
    sesion = db_session.create_session()
    user = sesion.query(User).filter(User.id == id).first()
    user.password = config.hashing(password)
    sesion.commit()
    sesion.close()
    return jsonify({'answer': 'ok'})


@blueprint.route('/api/user_set_name/', methods=['POST'])
def set_user_name():
    req = request.json
    id = req['id']
    new_name = req['new_name']
    User.set_name(id, new_name)
    return jsonify(
        {'answer': f'successfully set name '
         }
    )


@blueprint.route('/api/user_set_nomer', methods=['POST'])
def set_user_n():
    req = request.json
    id = req['id']
    nomer = req['nomer']
    user = User.user_from_id(id)
    user.set_nomer(nomer)
    return jsonify(
        {'answer': f'successfully set nomer'
         }
    )


@blueprint.route('/api/user_get_themes/<int:id>', methods=['GET'])
def get_themes_from_user(id):
    user = User.user_from_id(id)
    themes = user.all_themes()
    return jsonify(
        {
            'answer': themes
        }
    )


@blueprint.route('/api/user_set_name/<int:nomer>', methods=['GET'])
def get_user_from_nomer(nomer):
    id = User.id_from_nomer(nomer)
    if not id.isdigit():
        return id
    user = User.user_from_id(id)
    return jsonify(
        {
            user.to_dict()
        }
    )


@blueprint.route('/api/id', methods=['GET'])
def get_id_from_nomer():
    res = request.json
    nomer = res['nomer']
    answer = User.id_from_nomer(nomer)
    return answer


@blueprint.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(
                User.hashed_nomer == config.hashing(form.number.data)).first():
            return render_template('register.html',
                                   form=form,
                                   message="пользователь с таким номером уже есть")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        form.number.data = '7' + form.number.data[1:]
        user = User(
            name=form.name.data,
            hashed_nomer=config.hashing(form.number.data),
            password=config.hashing(form.password.data))
        db_sess.add(user)
        db_sess.commit()
        id = user.id
        db_sess.close()
        Theme.add_theme(header='всякое', user_id=id)
        return redirect('/')
    return render_template('register.html', title1='Регистрация', form=form,
                           message='пройдите регистрацию')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        form.nomer.data = '7' + form.nomer.data[1:]
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.hashed_nomer == config.hashing(form.nomer.data)).first()
        if user and user.password == config.hashing(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title1='Авторизация', form=form)
