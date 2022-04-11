import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from data import db_session
from . import Theme


class Note(SqlAlchemyBase):
    # в заметке должны быть короткие идеи,мысли,ссылки на другие заметки или темы
    __tablename__ = 'note'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("theme.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    links = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    header = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    theme = orm.relation('Theme')

    @classmethod
    def ides_from_names(cls, names, session=''):
        session = db_session.create_session() if not session else session
        links_ides = session.query(Note.id).where(Note.header.in_(names)).all()
        ides = ''
        for i in links_ides:
            ides += str(i[0]) + ' '
        session.close()
        return ides

    @classmethod
    def del_note(cls, note_id):
        session = db_session.create_session()
        dels = session.query(Note).filter(Note.id == note_id).delete(synchronize_session='evaluate')
        session.commit()

    def rename_note(self, header):
        self.header = header

    def get_links(self):
        return self.links.split()

    def get_theme(self):
        return self.theme
