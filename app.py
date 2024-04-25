from flask import Flask
from flask import render_template, redirect
from werkzeug.security import generate_password_hash

import db_session
from forms import RegisterForm, LoginForm
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_super_secret_key'


@app.route('/')
def root():
    return render_template("index.html")


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')

    return render_template('login.html', form=form)
