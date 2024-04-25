import sqlalchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from wtforms.validators import ValidationError

import db_session
from models import User


class RegisterForm(FlaskForm):
    """
    Форма регистрации нового пользователя
    """
    username = StringField('Имя', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Пароль (подтверждение)', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        s = db_session.create_session()
        user = s.scalar(sqlalchemy.select(User).where(User.login == login.data))
        if user is not None:
            raise ValidationError('Такой логин уже занят. Придумайте другой Ж:)')


class LoginForm(FlaskForm):
    """
    Форма логина
    """
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
