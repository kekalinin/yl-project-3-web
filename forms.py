from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.validators import ValidationError


class RegisterForm(FlaskForm):
    class Meta:
        locales = ['ru_RU', 'ru']

    username = StringField('Имя', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password1 = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=6, max=10)])
    password2 = PasswordField('Пароль (подтверждение)', validators=[
        DataRequired(),
        Length(min=6, max=10),
        EqualTo('password1', message='Пароли должны совпадать')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == username.data).count() == 0:
            raise ValidationError('Такого пользователя нет!')
