import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data import db_session, Note
from data.db_session import SqlAlchemyBase


class Theme(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'theme'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    header = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user = orm.relation('User')  # когда будет юзер надо будет вернуть
    orm.relation("Note", back_populates='theme')

    # тема может содержать сколько угодно идей/заметок
    @classmethod
    def add_theme(cls, header, user_id):
        session = db_session.create_session()
        if session.query(Theme).filter(Theme.header == header).first():
            return f'theme with header {header} already exist'
        theme = Theme(header=header, user_id=user_id)
        session.add(theme)
        session.commit()
        session.close()
        return f'successfully added theme {header}'

    @classmethod
    def del_theme(cls, theme_id, user_id, anything=10 ** 9 + 1):
        print(theme_id)
        session = db_session.create_session()
        cls.add_theme('всякое', user_id)
        if anything == 10 ** 9 + 1:
            anything = session.query(Theme).filter(Theme.header == 'всякое').first()
        elif not session.query(Theme).filter(Theme.header == anything).first():
            cls.add_theme(anything, user_id)
        theme = session.query(Theme).filter(Theme.id == theme_id)
        session.close()
        if theme and theme.first():
            for i in theme.first().get_notes():
                # для каждой заметки удалённой темы меняем её тему на данную либо стандартную
                session = db_session.create_session()
                i.theme = anything
                i.theme_id = anything.id
                session.merge(i)
                session.commit()
                session.close()
        else:
            return f'ERROR: not theme {theme.first().header} '
        session = db_session.create_session()
        session.query(Theme).filter(Theme.id == theme_id).delete()
        session.commit()
        session.close()
        return f'successfully deleted/changed theme {theme.first().header}'

    @classmethod
    def theme_from_id(cls, id):
        session = db_session.create_session()
        theme = session.query(Theme).filter(Theme.id == id).first()
        session.close()
        return theme

    def add_note(self, text='', links=[], header=''):
        session = db_session.create_session()
        note1 = session.query(Note.Note).filter(
            Note.Note.theme_id == self.id).filter(Note.Note.header == header).first()
        links = Note.Note.ides_from_names(links) if isinstance(links, list) else links
        if note1:
            note1.links = links
            note1.text = text
        else:
            new_note = Note.Note(text=text, header=header, links=links, theme=self)
            session.add(new_note)
        session.commit()
        session.close()


    # надо будет добавить юзера

    def get_notes(self):
        session = db_session.create_session()
        notes = session.query(Note.Note).filter(Note.Note.theme_id == self.id).all()
        return notes

    def communicate_level(self):
        session = db_session.create_session()
        notes = self.get_notes()
        d1 = {}
        for note in notes:
            for link in note.get_links():
                note2 = session.query(Note.Note).filter(Note.Note.id == int(link)).first()
                if note2 and note2.theme_id != self.id:
                    if note2.theme_id not in d1.keys():
                        d1[note2.theme_id] = 1
                    else:
                        d1[note2.theme_id] += 1
        return d1
