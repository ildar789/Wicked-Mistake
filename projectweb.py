from random import choice
from flask import Flask, render_template, url_for, request
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.utils import redirect
from data import db_session
from data.news import News, NewsForm
from data.registry import RegisterForm, LoginForm
from data.users import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'wicked_mistake_secret_key'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/') # ОТОБРАЖЕНИЕ СОЗДАННЫХ НОВОСТЕЙ
def index():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private != True)
    return render_template("mainindexx.html", news=news)


@app.route('/faq') # ИНФОРМАЦИЯ О НАС
def faq():
    return render_template('faq.html')


@app.route('/register', methods=['GET', 'POST']) # РЕГИСТРАЦИЯ
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


@app.route("/news", methods=["GET", "POST"]) # СОЗДАНИЕ НОВОСТЕЙ
@login_required
def add_news():
    form = NewsForm()
    if request.method == "GET":
        return render_template("add_news.html", title="Добавление новости",
                               form=form)
    elif request.method == "POST":
        session = db_session.create_session()
        news = News()
        news.title = request.form.get("title")
        news.theme = request.form.get("theme")
        news.content = request.form.get("content")
        news.user_id = current_user.id
        private = request.form.get("private")
        news.is_private = 0 if private is None else 1
        session.add(news)
        session.commit()
        return redirect("/")


@app.route("/news/<int:id>", methods=["GET", "POST"]) # ИЗМЕНЕНИЕ НОВОСТИ
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            form.title = news.title
            form.theme = news.theme
            form.content = news.content
            form.is_private = news.is_private
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = request.form.get("title")
            news.theme = request.form.get("theme")
            news.content = request.form.get("content")
            private = request.form.get("private")
            news.is_private = 0 if private is None else 1
            session.commit()
            return redirect("/")
    return render_template("news_edit.html", title="Редактирование новости", form=form)


@app.route("/news_delete/<int:id>", methods=["GET", "POST"]) # УДАЛЕНИЕ НОВОСТИ
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    news_all = session.query(News).filter(News.user == current_user).all()
    if len(news_all) >= 2:
        redirect_to = news_all[news_all.index(news) - 1].id
    else:
        redirect_to = 0
    if news:
        session.delete(news)
        session.commit()
    return redirect(f"/#{redirect_to}")


@app.route('/profile') # ПРОФИЛЬ УЧАСТНИКА
def prof():
    form = LoginForm()
    return render_template('profile.html', form=form)


@app.route('/login', methods=['GET', 'POST']) # АВТОРИЗАЦИЯ
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


@app.route('/logout') # ВЫХОД ИЗ УЧЁТНОЙ ЗАПИСИ
@login_required
def logout():
    logout_user()
    return redirect("/")


db_session.global_init("db/steam.sqlite")
if __name__ == '__main__':
    app.run()
