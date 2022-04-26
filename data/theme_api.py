from flask_login import current_user, login_required
from sqlalchemy import orm
from werkzeug.utils import redirect

import config
import flask
from flask import jsonify, request, render_template
from requests import get, post

from data import db_session
from data.Note import Note
from data.Theme import Theme
from data.User import User
from form import login
from form.add_note import AddNoteForm
from form.add_theme import AddThemeForm

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
            'answer': [note.header for note in notes]
        }
    )


@blueprint.route('/show_note_theme/<int:id>', methods=['GET'])
def get_notes_thm(id):
    theme = Theme.theme_from_id(id)
    notes = theme.get_notes()
    n = 5
    notes_in_notes = [[] for _ in range(len(notes) // n + 1)]
    k = 0
    session = db_session.create_session()

    for i in range(1, len(notes) + 1):
        if notes[i - 1].links:
            links = notes[i - 1].links.split()
            header_id_links = []
            for link_id in links:
                if link_id and link_id.isdigit():
                    link = session.query(Note).filter(Note.id == link_id).first()
                    if link:
                        header_id_links.append((link.header, link.theme_id, link.id))
            notes[i - 1].any = header_id_links
        notes_in_notes[k].append(notes[i - 1])
        if not i % n:
            k += 1
    session.expunge_all()
    session.close()
    return render_template('show_notes.html', notes=notes_in_notes)


@blueprint.route('/show_note_theme1/<int:id>/<int:con1>', methods=['GET', 'POST','PUT','DELETE'])
def get_notes_thm1(id, con1):
    theme = Theme.theme_from_id(id)
    notes = theme.get_notes()
    n = 5
    notes_in_notes = [[] for _ in range(len(notes) // n + 1)]
    k = 0
    session = db_session.create_session()

    for i in range(1, len(notes) + 1):
        if notes[i - 1].links:
            links = notes[i - 1].links.split()
            header_id_links = []
            for link_id in links:
                if link_id and link_id.isdigit():
                    link = session.query(Note).filter(Note.id == link_id).first()
                    if link:
                        header_id_links.append((link.header, link.theme_id, link.id))
            notes[i - 1].any = header_id_links
        notes_in_notes[k].append(notes[i - 1])
        if not i % n:
            k += 1
    session.expunge_all()
    session.close()
    return render_template('show_con_note.html', notes=notes_in_notes, real_note=con1)


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


@blueprint.route('/del_theme/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_theme(id):
    user_id = current_user.id
    res = post(config.address + '/api/del_theme/', json={'id': id, 'user_id': user_id}).json()[
        'answer']
    return redirect('/')


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


@blueprint.route('/add_theme', methods=['POST', 'GET'])
@login_required
def add_theme_form():
    form = AddThemeForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(Theme).filter(Theme.user_id == current_user.id, Theme.header ==
                                                                         form.header.data).first():
            return render_template('create_theme.html',
                                   form=form, message='тема с таким названием уже существует')
        Theme.add_theme(header=form.header.data, user_id=current_user.id)
        return redirect('/')
    return render_template('create_theme.html', form=form)


@blueprint.route(f'/create_note/<int:id>', methods=['POST', 'GET'])
@login_required
def cr_note(id):
    form = AddNoteForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        note = db_sess.query(Note).filter(Note.header == form.header.data).filter(
            Note.theme_id == id).first()
        if note:
            return render_template('create_note.html',
                                   message="заметка с таким названием в этой теме уже существует",
                                   form=form)
        # id = req['id']
        #     new_links = req['new_links']
        #     user_id = req['user_id']
        new_note = Note(text=form.text.data, header=form.header.data, links='',
                        theme=db_sess.query(Theme).filter(Theme.id == id).first())
        db_sess.add(new_note)
        db_sess.commit()
        id1 = new_note.id
        if form.links.data:
            form.links.data.strip()
            if form.links.data[-1] == '/':
                form.links.data = form.links.data[:-1]
            form.links.data.strip()
        db_sess.close()
        user_id = current_user.id
        new_links = form.links.data.replace('/', '~')
        req = '/api/add_links/'
        post(config.address + req, json={'id': id1, 'new_links': new_links, 'user_id': user_id})
        return redirect(f'/show_note_theme/{id}')
    return render_template('create_note.html', title1='Авторизация', form=form)
