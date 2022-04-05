from flask import render_template, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user
from app.app import MainApp
from data.db_session import create_session
from forms.login_form import LoginForm
from forms.gcd_form import GcdForm
from data.users import User
from forms.register_form import RegisterForm
from flask_restful import Api
from tools.login_resources import RegisterRes, LoginRes, Dude
from tools.math import one_arg_resources, two_args_resources
import requests

app = MainApp(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
api.add_resource(RegisterRes, '/api/v2/register')
api.add_resource(LoginRes, '/api/v2/login')
api.add_resource(one_arg_resources.FactorialRes, '/api/v2/math/factorial')
api.add_resource(one_arg_resources.FactorizationRes, '/api/v2/math/factorization')
api.add_resource(two_args_resources.GCDRes, '/api/v2/math/gcd')
api.add_resource(two_args_resources.LCMRes, '/api/v2/math/lcm')
api.add_resource(Dude, '/api/v2/dude')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Deskmate')


@app.route('/creators')
def creators():
    return render_template('creators.html', title='Deskmate')


@app.route('/history')
def history():
    buttons = {'Изменить список дат': 'change_dates',
               'Тренажер': 'trening',
               'Импортировать даты': 'import_dates'}
    return render_template('subject.html', title='Deskmate', sbj='История', btns=buttons)


@app.route('/algebra')
def algebra():
    buttons = {'НОД и НОК': 'gcd',
               'Разложить на простые': 'factorization'}
    return render_template('subject.html', title='Deskmate', sbj='Алгебра', btns=buttons)


@app.route('/gcd', methods=['GET', 'POST'])
def gcd_page():
    form = GcdForm()
    params = {'title': "НОД и НОК", 'form' : form}
    if form.validate_on_submit():
        gcd_data = {'a': form.first_number.data, 'b': form.second_number.data}
        result_gcd = requests.get('http://localhost:8080/api/v2/math/gcd', data=gcd_data).json()
        result_lcm = requests.get('http://localhost:8080/api/v2/math/lcm', data=gcd_data).json()

        if result_gcd['success'] == 'OK':
            params['result_gcd'] = result_gcd['result']
        else:
            params['message'] = result_gcd['message']

        if result_lcm['success'] == 'OK':
            params['result_lcm'] = result_lcm['result']
        else:
            params['message'] = result_lcm['message']

        return render_template('gcd.html', **params)
    return render_template('gcd.html', **params)


@app.route('/geometry')
def geometry():
    buttons = {'Найти синус и косинус угла': 'sin_cos'}
    return render_template('subject.html', title='Deskmate', sbj='Геометрия', btns=buttons)


@app.route('/informatics')
def informatics():
    buttons = {'Построить таблицу истинности': 'create_table',
               'Перевод между разными системами счисления' : 'translate'}
    return render_template('subject.html', title='Deskmate', sbj='Информатика', btns=buttons)


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


@app.route('/algebra')
def algebra_page():
    return render_template('algebra.html', title='Математика')


@app.route('/success')
def success():
    return 'success'


@login_manager.user_loader
def load_user(user_id: int):
    session = create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
