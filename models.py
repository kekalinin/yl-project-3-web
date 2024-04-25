import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from db_session import SqlAlchemyBase


class User(UserMixin, SqlAlchemyBase):
    """
    Пользователь приложения
    """
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_dt = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    photos = orm.relationship("Photo", back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Photo(SqlAlchemyBase):
    """
    Фотография пользователя
    """
    __tablename__ = 'photos'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.BLOB)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_dt = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    tags = orm.relationship('Tag', secondary="photos_tags", backref="photos")


class Tag(SqlAlchemyBase):
    """
    Метка в фотографии
    """
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, index=True)


"""
Связь много-ко-многим между фотографией и меткой.
"""
PhotoTags = sqlalchemy.Table(
    'photos_tags',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('photo', sqlalchemy.Integer, sqlalchemy.ForeignKey('photos.id')),
    sqlalchemy.Column('tag', sqlalchemy.Integer, sqlalchemy.ForeignKey('tags.id'))
)
