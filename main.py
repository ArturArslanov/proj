import logging

from flask import Flask
from flask_login import login_manager, login_required, logout_user
from werkzeug.utils import redirect

from data import noteapi
from config import bd_path
from data import db_session, user_api, theme_api
from data.User import User

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/')
def index():
    return 'да'



def main():
    db_session.global_init(bd_path)
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(theme_api.blueprint)
    app.register_blueprint(noteapi.blueprint)
    app.run(port=8089, host='127.0.0.1')



if __name__ == "__main__":
    main()
