import base64

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort
)
from flask_login import (
    logout_user,
    LoginManager,
    login_user,
    current_user,
    login_required
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
    """
    Главная страница
    """
    s = db_session.create_session()
    q = s.query(models.Photo)
    if not current_user.is_authenticated:
        q = q.filter(models.Photo.is_private.is_(False))
    photos = q.order_by(
        models.Photo.created_dt.desc()).limit(10).all()
    return render_template('index.html', photos=photos)


#
# Работа с пользователем
#

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


#
# Фотографии
#

def get_or_create(session, model, **kwargs):
    """
    Находит в БД указанные объект или создает его, если не найдено.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


@app.route('/photos/add', methods=['GET', 'POST'])
@login_required
def photo_add():
    """
    Добавление фотографий пользователя
    """
    form = forms.NewPhotoForm()
    if form.validate_on_submit():
        image = request.files[form.content.name].read()
        p = models.Photo(
            title=form.title.data,
            content=image,
            is_private=form.is_private.data,
            user_id=current_user.id,
        )
        s = db_session.create_session()
        tags = []
        for tag in form.tags.data.split(' '):
            tags.append(get_or_create(s, models.Tag, name=tag))
        p.tags = tags
        s.add(p)
        s.commit()
        flash('Фотография добавлена')
        return redirect(url_for('index'))
    return render_template('photo_add.html', title='Новая фотка', form=form)


@app.route('/photos/<id>')
def photo(id):
    """
    Показывает фотографию с указанным номером
    """
    s = db_session.create_session()

    q = s.query(models.Photo)
    if not current_user.is_authenticated:
        q = q.filter(models.Photo.is_private.is_(False))
    p = q.filter(models.Photo.id == id).first()
    # если не нашли фотографию, возвращаем ошибку 404
    if not p:
        abort(404)
    img64 = base64.b64encode(p.content).decode('utf-8')
    return render_template('photo.html', photo=p, img64=img64)


@app.route('/photos/del/<id>')
@login_required
def photo_del(id):
    """
    Удаление фотографии пользователя
    """
    s = db_session.create_session()
    p = s.query(models.Photo).filter(models.Photo.id == id).first()
    if p.user.id != current_user.id:
        abort(403)
    s.delete(p)
    s.commit()
    flash('Фотография удалена')
    return redirect(url_for('index'))


@app.route('/photos/tags/<tag>')
def tags(tag):
    """
    Показывает фотографии с тэгом.
    """
    s = db_session.create_session()
    t = s.query(models.Tag).filter(models.Tag.name == tag).first()
    return render_template('tag.html', tag=tag, photos=t.photos)


@app.route('/photos/user/<login>')
def photo_from_user(login):
    """
    Показывает фотографии, созданные указанным пользователем.
    """
    s = db_session.create_session()
    usr = s.query(models.User).filter(models.User.login == login).first()
    if not usr:
        abort(404)
    q = s.query(models.Photo).filter(models.Photo.user == usr)
    if not current_user.is_authenticated:
        q = q.filter(models.Photo.is_private.is_(False))
    photos = q.all()
    return render_template('photo_from_user.html', login=login, photos=photos)
