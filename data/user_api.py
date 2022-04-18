import flask
from flask import jsonify, request

from data import db_session
from data.Theme import Theme
from data.User import User

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
    answer = User.add_user(name, nomer)
    if 'tele_id' in req.keys():
        id = req['tele_id']
        User.set_id(nomer, id)
    Theme.add_theme(header='всякое', user_id=id)
    return jsonify({
        'answer': answer
    })


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
