import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase
from data import db_session
from config import hashing
from data.Theme import Theme


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_nomer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    orm.relation("User", back_populates='user')

    @classmethod
    def add_user(cls, name, nomer):
        session = db_session.create_session()
        if not cls.id_from_nomer(nomer) == f'not user with this nomer {nomer}':
            return 'user with this nomer already exist'
        user = User(name=name, hashed_nomer=hashing(nomer))
        session.add(user)
        session.commit()
        session.close()
        return f'successfully added user {name}'

    @classmethod
    def set_name(cls, id, new_name):
        session = db_session.create_session()
        user = session.query(cls).filter(cls.id == id).first()
        user.name = new_name
        session.commit()
        session.close()

    @classmethod
    def set_nomer(cls, id, nomer):
        session = db_session.create_session()
        user = session.query(cls).filter(cls.id == id).first()
        user.hashed_nomer = hashing(nomer)
        session.commit()
        session.close()

    def check_nomer(self, password):
        return self.hashed_nomer == hashing(password)

    def all_themes(self):
        session = db_session.create_session()
        themes = session.query(Theme).filter(Theme.user_id == self.id).all()

        session.close()
        return [theme.id for theme in themes]

    @classmethod
    def user_from_id(cls, id):
        session = db_session.create_session()
        user = session.query(User).filter(User.id == id).first()
        session.close()
        return user

    @classmethod
    def id_from_nomer(cls, nomer):
        session = db_session.create_session()
        id = session.query(User.id).filter(
            User.hashed_nomer == hashing(nomer)).first()
        if id:
            return id
        else:
            return f'not user with this nomer {nomer}'

    @classmethod
    def set_id(cls, nomer, tele_id):
        session = db_session.create_session()
        user = session.query(User).filter(User.hashed_nomer == hashing(nomer)).first()
        user.id = tele_id
        session.commit()
        session.close()
