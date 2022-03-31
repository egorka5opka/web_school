from flask import render_template, redirect, jsonify
from flask_login import LoginManager
from app.app import MainApp
from forms.login_form import LoginForm
from data.users import User
from forms.register_form import RegisterForm
from flask_restful import Api
from tools.login_resources import RegisterRes, LoginRes
from tools.user_resources import UserRes
import requests
import json

app = MainApp(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
api.add_resource(RegisterRes, '/api/v2/register')
api.add_resource(LoginRes, '/api/v2/login')
api.add_resource(UserRes, '/api/v2/user')


@app.route("/")
def root():
    return "main page"


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    params = {"title": "Вход",
              "form": form}
    return render_template('login.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    params = {"title": "Регистрация",
              "form": form}
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            params['message'] = 'Пароли не совпадают'
            return render_template('register.html', **params)
        register_data = {'login': form.login.data,
                         'password': form.password.data}
        requests.post('http://localhost:8080/api/v2/register',
                      data=register_data)
        return redirect("/success")
    return render_template('register.html', **params)


@app.route("/success")
def success():
    return "success"


@login_manager.user_loader
def load_user(user_id):
    db_sess = app.db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
