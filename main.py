from codecs import decode

from flask import render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app.app import MainApp
from data.db_session import create_session
from forms.import_form import ImportForm
from forms.login_form import LoginForm
from data.users import User
from forms.register_form import RegisterForm
from forms.history_event_from import EventForm
from flask_restful import Api
from tools.login_resources import RegisterRes, LoginRes, Dude
from tools.math import one_arg_resources, two_args_resources
from tools.history.history_resources import HistoryListRes, HistoryEventRes
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
api.add_resource(HistoryListRes, '/api/v2/history/event')
api.add_resource(HistoryEventRes, '/api/v2/history/event/<int:event_id>')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Deskmate')


@app.route('/creators')
def creators():
    return render_template('creators.html', title='Deskmate')


@app.route('/history')
def history():
    buttons = {'Список дат': '/history/events',
               'Тренажер': '/history/training',
               'Импортировать даты': '/history/import'}
    return render_template('subject.html', title='История', sbj='История', btns=buttons)


@app.route('/history/events')
@login_required
def history_events():
    events = requests.get('http://localhost:8080/api/v2/history/event').json()
    params = {'title': 'Deskmate', 'events': list(filter(lambda e: e['user_id'] == current_user.id, events))}
    return render_template('history_events.html', **params)


@app.route('/history/event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    form = EventForm()
    params = {'title': 'История', 'btn': 'Изменить'}
    if request.method == 'GET':
        response = requests.get(f'http://localhost:8080/api/v2/history/event/{event_id}').json()
        if response.get('success', 'failed') == 'failed':
            abort(404)
        event = response.get('event')
        params['title'] = event['event']
        form.year.data = event.get('year', None)
        form.event.data = event.get('event', None)
        form.description.data = event.get('description', None)
    params['form'] = form
    if form.validate_on_submit():
        data = {'year': form.year.data,
                'event': form.event.data,
                'description': form.description.data,
                'user_id': current_user.id}
        result = requests.post(f'http://localhost:8080/api/v2/history/event/{event_id}', data=data).json()
        if result.get('success', 'failed') == 'OK':
            return redirect('/history/events')
        params['message'] = result.get('message', 'Непердвиденная ошибка')
    return render_template('new_event.html', **params)


@app.route('/history/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    params = {'title': 'История',
              'form': form,
              'btn': 'Создать'}
    if form.validate_on_submit():
        data = {'year': form.year.data,
                'event': form.event.data,
                'description': form.description.data,
                'user_id': current_user.id}
        result = requests.post('http://localhost:8080/api/v2/history/event', data=data).json()
        if result.get('success', 'failed') == 'OK':
            return redirect('/history/events')
        params['message'] = result.get('message', 'Непердвиденная ошибка')
    return render_template('new_event.html', **params)


@app.route('/history/delete/<int:event_id>')
@login_required
def delete_event(event_id):
    result = requests.delete(f'http://localhost:8080/api/v2/history/event/{event_id}').json()
    if result.get('success', 'failed') == 'failed':
        abort(404)
    return redirect('/history/events')


@app.route('/history/import', methods=['GET', 'POST'])
@login_required
def import_events():
    form = ImportForm()
    params = {'title': 'Импорт событий',
              'form': form}
    if form.validate_on_submit():
        f = form.file.data.stream
        f2 = f.read().decode('utf-8')
        lines = [line.strip() for line in f2.split('\n')]
        i = 0
        while i < len(lines):
            title, year = lines[i].split(';')
            i += 1
            text = ''
            while i < len(lines):
                text += lines[i]
                i += 1
                if text.endswith('*/'):
                    break
            data = {'year': int(year.strip()),
                    'event': title,
                    'description': text,
                    'user_id': current_user.id}
            result = requests.post('http://localhost:8080/api/v2/history/event', data=data).json()
            if result.get('success', 'failed') == 'failed':
                params['message'] = result.get('message', 'Непердвиденная ошибка')
                break
        else:
            return redirect('/history/events')
    return render_template('import_events.html', **params)


@app.route('/algebra')
def algebra():
    buttons = {'НОД и НОК': 'gcd',
               'Разложить на простые': 'factorization'}
    return render_template('subject.html', title='Deskmate', sbj='Алгебра', btns=buttons)


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
