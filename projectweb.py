import os
from random import choice

from flask import Flask, render_template, url_for
from flask_login import LoginManager, login_required, logout_user, login_user
from flask_mail import Mail
from werkzeug.utils import redirect

from data import db_session
from data.news import News
# from data.maily import send_password_reset_email
from data.registry import RegisterForm, LoginForm
from data.users import User

app = Flask(__name__)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private != True)
    return render_template("mainindexx.html", news=news)


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    session = db_session.create_session()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registry.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('registry.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, surname=form.surname.data,
                    email=form.email.data, schizm=form.schizm.data)
        user.set_password(form.password.data)
        user.photo = url_for("static", filename=f"img/{choice(['one', 'two', 'three', 'four'])}.jpg")
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('registry.html', title='Регистрация', form=form)


@app.route('/profile')
def prof():
    form = LoginForm()
    return render_template('profile.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


'''''@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Проверьте свою почту')
        return redirect(url_for('login'))
    return render_template('reset_password.html',
                           title='Сброс и изменение пароля', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)'''''


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


db_session.global_init("db/steam.sqlite")
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(threaded=True, port=5000)
