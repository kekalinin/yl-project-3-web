from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.validators import ValidationError

import db_session
from users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_super_secret_key'


@app.route('/')
def root():
    return render_template("index.html")


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.login = form.login.data
        user.username = form.username.data
        user.hashed_password = generate_password_hash(form.password1.data)
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', form=form)


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == username.data).count() == 0:
            raise ValidationError('Такого пользователя нет!')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')

    return render_template('login.html', form=form)


if __name__ == '__main__':
    db_session.global_init("data/photo.db")

    app.run(port=8080, host='127.0.0.1')
