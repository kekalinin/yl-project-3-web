from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash
)
from flask_login import (
    logout_user,
    LoginManager,
    login_user,
    current_user,
    # login_required
)

import db_session
import forms
import models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_super_secret_key'

# Иницализируем LoginManager, который управляет процессом авторизации пользователя.
lm = LoginManager(app)
# Указываем на какой странице будет логин для пользователя.
lm.login_view = 'login'


@lm.user_loader
def load_user(id):
    """
    Функция для получения пользователя из БД
    """
    s = db_session.create_session()
    return s.get(models.User, int(id))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Создание пользователя
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        u = models.User(username=form.username.data, login=form.login.data)
        u.set_password(form.password.data)
        s = db_session.create_session()

        s.add(u)
        s.commit()
        flash('Поздравляем! Вы теперь зарегистрированный пользователь!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация нового пользователя', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Вход в приложение
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        s = db_session.create_session()
        usr = s.scalar(
            s.query(models.User).where(models.User.login == form.login.data))
        if usr is None or not usr.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(usr, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Вход в альбом', form=form)


@app.route('/logout')
def logout():
    """
    Выход пользователя
    """
    logout_user()
    return redirect(url_for('index'))
