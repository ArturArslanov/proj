import config
import flask
from flask import jsonify, request
from requests import get

from data import db_session
from data.Theme import Theme

blueprint = flask.Blueprint(
    'theme_api',
    __name__,
    template_folder='../template'
)


@blueprint.route('/api/theme_add/', methods=['POST'])
def add_theme():
    req = request.json
    header = req['header']
    user_id = req['user_id']
    answer = Theme.add_theme(header=header, user_id=user_id)
    return jsonify({
        'answer': answer
    }
    )


@blueprint.route('/api/set_theme_header/', methods=['POST', 'PUT'])
def set_theme_header():
    req = request.json
    id = req['id']
    header = req['header']

    session = db_session.create_session()
    theme = session.query(Theme).filter(Theme.id == id).first()
    theme.header = header
    session.commit()
    session.close()
    return jsonify(
        {'answer': f'successfully set header'
         }
    )


@blueprint.route('/api/user_get_notes/<int:id>', methods=['GET'])
def get_notes(id):
    theme = Theme.theme_from_id(id)
    notes = theme.get_notes()
    return jsonify(
        {
            'answer': notes
        }
    )


@blueprint.route('/api/theme_communicate_level/<int:id>', methods=['GET'])
def comm_level(id):
    theme = Theme.theme_from_id(id)
    answer = theme.communicate_level()
    return jsonify(
        {
            'answer': answer
        }
    )


@blueprint.route('/api/del_theme/', methods=['DELETE', 'POST'])
def del_theme():
    req = request.json
    id = req['id']
    user_id = req['user_id']
    answer = Theme.del_theme(id, user_id)
    return jsonify({'answer': answer})


@blueprint.route('/api/set_theme/', methods=['POST', 'PUT'])
def set_theme():
    req = request.json
    id = req['id']
    user_id = req['user_id']
    new_id = req['new_id']
    answer = Theme.del_theme(id, user_id, new_id)
    return jsonify({'answer': answer})


@blueprint.route('/api/theme_header/<int:id>', methods=['GET'])
def get_name(id):
    theme = Theme.theme_from_id(id)
    return jsonify({'answer': theme.header})


@blueprint.route('/api/id_from_header/<int:user_id>/<string:header>', methods=['GET'])
def id_from_header(user_id, header):
    s1 = get(config.address + f'api/user_get_themes/{user_id}').json()['answer']
    for i in s1:
        theme = Theme.theme_from_id(i)
        if theme.header == header:
            return jsonify({"answer": f"{i}"})
    return jsonify({'answer': 'not exist theme with this header'})


@blueprint.route('/api/add_note/', methods=['POST', 'PUT'])
def add_note():
    req = request.json
    theme_id = req['theme_id']
    header = req['header']
    theme = Theme.theme_from_id(theme_id)
    theme.add_note(text=' ', links=' ', header=header)
    return jsonify({'answer': 'yes'})
