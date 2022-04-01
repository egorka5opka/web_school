from flask import render_template, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user
from app.app import MainApp
from data.db_session import create_session
from forms.login_form import LoginForm
from data.users import User
from forms.register_form import RegisterForm
from flask_restful import Api
from tools.login_resources import RegisterRes, LoginRes
import requests

app = MainApp(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
api.add_resource(RegisterRes, '/api/v2/register')
api.add_resource(LoginRes, '/api/v2/login')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Deskmate')


@app.route('/creators')
def creators():
    return render_template('creators.html', title='Deskmate')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = {'title': 'Вход',
              'form': form}
    if form.validate_on_submit():
        login_data = {'login': form.login.data,
                      'password': form.password.data}
        result = requests.post('http://localhost:8080/api/v2/login', data=login_data).json()
        if result['success'] == 'OK':
            login_user(load_user(result['user']['id']), remember=True)
            return redirect('/')
        params['message'] = result['message']
        return render_template('login.html', **params)
    return render_template('login.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    params = {'title': 'Регистрация',
              'form': form}
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            params['message'] = 'Пароли не совпадают'
            return render_template('register.html', **params)
        register_data = {'login': form.login.data,
                         'password': form.password.data}
        result = requests.post('http://localhost:8080/api/v2/register', data=register_data).json()
        if result['success'] == 'OK':
            login_user(load_user(result['user']['id']), remember=True)
            return redirect('/')
        params['message'] = result['message']
        return render_template('register.html', **params)

    return render_template('register.html', **params)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/success')
def success():
    return 'success'


@login_manager.user_loader
def load_user(user_id: int):
    session = create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
