import logging

import config
from flask import Flask, render_template, make_response, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from requests import get
from werkzeug.utils import redirect

from data import noteapi
from config import bd_path, secret_key
from data import db_session, user_api, theme_api
from data.Theme import Theme
from data.User import User

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
login_manager = LoginManager()
login_manager.init_app(app)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/arzetel/')
@app.route('/')
def index():
    themes = []
    if current_user.is_authenticated:
        req = f'api/user_get_themes/{current_user.id}'
        themes_ides = get(config.address + req).json()['answer']
        mini_thems = []
        n = 5
        for i in range(1, len(themes_ides) + 1):
            theme = Theme.theme_from_id(themes_ides[i - 1])

            if theme:
                mini_thems.append(theme)
            if not i % n:
                themes.append(mini_thems.copy())
                mini_thems.clear()
        if mini_thems:
            themes.append(mini_thems.copy())
            mini_thems.clear()
    return render_template('new.html', themes=themes)


def main():
    db_session.global_init(bd_path)
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(theme_api.blueprint)
    app.register_blueprint(noteapi.blueprint)
    app.run(port=8089, host='127.0.0.1')


if __name__ == "__main__":
    main()
