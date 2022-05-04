import os
from flask import render_template, redirect, request, abort, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import func

from app.app import MainApp
from data.db_session import create_session
from data.history_events import HistoryEvent
from forms.import_form import ImportForm
from forms.login_form import LoginForm
from forms.gcd_form import GcdForm
from forms.factorization_form import FactorizationForm
from forms.geron_from import GeronForm
from forms.create_table import CreateTableForm
from forms.training_form import TrainingForm
from forms.translate_form import TranslateForm
from data.users import User
from forms.register_form import RegisterForm
from forms.history_event_from import EventForm
from flask_restful import Api
from tools.history.history_resources import HistoryListRes, HistoryEventRes
from tools.login_resources import RegisterRes, LoginRes, Dude
from tools.math import one_arg_resources, two_args_resources, three_args_resources, inf_one_arg_resources, \
    inf_three_arg_resources
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
api.add_resource(three_args_resources.GeronRes, '/api/v2/math/geron')
api.add_resource(inf_one_arg_resources.TruthTable, '/api/v2/inf/truth_table')
api.add_resource(inf_three_arg_resources.Translation, '/api/v2/inf/traslate')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='webmate')


@app.route('/creators')
def creators():
    return render_template('creators.html', title='webmate')


@app.route('/history')
def history():
    buttons = {'Список дат': '/history/events',
               'Тренажер': '/history/training',
               'Импортировать даты': '/history/import'}
    return render_template('subject.html', title='История', sbj='История', btns=buttons)


@app.route('/history/events')
@login_required
def history_events():
    events = requests.get(f'http://localhost:{port}/api/v2/history/event').json()
    params = {'title': 'webmate', 'events': list(filter(lambda e: e['user_id'] == current_user.id, events))}
    return render_template('history_events.html', **params)


@app.route('/history/event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    form = EventForm()
    params = {'title': 'История', 'btn': 'Изменить'}
    if request.method == 'GET':
        response = requests.get(f'http://localhost:{port}/api/v2/history/event/{event_id}').json()
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
        result = requests.post(f'http://localhost:{port}/api/v2/history/event/{event_id}', data=data).json()
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
        result = requests.post(f'http://localhost:{port}/api/v2/history/event', data=data).json()
        if result.get('success', 'failed') == 'OK':
            return redirect('/history/events')
        params['message'] = result.get('message', 'Непердвиденная ошибка')
    return render_template('new_event.html', **params)


@app.route('/history/delete/<int:event_id>')
@login_required
def delete_event(event_id):
    result = requests.delete(f'http://localhost:{port}/api/v2/history/event/{event_id}').json()
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
        try:
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
                        text = text[:-2]
                        break
                data = {'year': int(year.strip()),
                        'event': title,
                        'description': text,
                        'user_id': current_user.id}
                result = requests.post(f'http://localhost:{port}/api/v2/history/event', data=data).json()
                if result.get('success', 'failed') == 'failed':
                    params['message'] = result.get('message', 'Непердвиденная ошибка')
                    break
            else:
                return redirect('/history/events')
        except BaseException as e:
            params['message'] = 'Не удалось прочитать файл'
    return render_template('import_events.html', **params)


@login_required
@app.route('/history/training', methods=['GET', 'POST'])
def training():
    form = TrainingForm()
    if form.validate_on_submit():
        question_id = int(request.cookies.get("event_id", 0))
        result = requests.get(f'http://localhost:{port}/api/v2/history/event/{question_id}').json()
        event = result['event']
        params = dict(title='Тренажер', **event)
        params['right'] = (event['year'] == form.year.data)
        res = make_response(render_template('training_response.html', **params))
        return res
    else:
        session = create_session()
        event = session.query(HistoryEvent).filter(HistoryEvent.user_id == current_user.id).\
            order_by(func.random()).first()
        if not event:
            return render_template('training_response.html', title='Тренажер', event='Ошибка',
                                   year='у вас нет ни одного события',
                                   description='Перейдите во вкладку история и создайте записи - исторические события')
        params = {'title': 'Тренажер',
                  'form': form,
                  'question': f'В каком году произошло событие "{event.event}"?'}
        res = make_response(render_template('training.html', **params))
        res.set_cookie('event_id', str(event.id), max_age=60 * 60)
        return res


@app.route('/algebra')
def algebra():
    buttons = {'НОД и НОК': 'gcd',
               'Разложить на простые': 'factorization',
               'Факториал числа': 'factorial'}
    return render_template('subject.html', title='webmate', sbj='Алгебра', btns=buttons)


@app.route('/gcd', methods=['GET', 'POST'])
def gcd_page():
    form = GcdForm()
    params = {'title': "НОД и НОК", 'form': form}
    if form.validate_on_submit():
        gcd_data = {'a': form.first_number.data, 'b': form.second_number.data}
        result_gcd = requests.get(f'http://localhost:{port}/api/v2/math/gcd', data=gcd_data).json()
        result_lcm = requests.get(f'http://localhost:{port}/api/v2/math/lcm', data=gcd_data).json()

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


@app.route('/factorization', methods=['GET', 'POST'])
def factorization_form():
    form = FactorizationForm()
    params = {'title': "Факторизация", 'form': form}
    if form.validate_on_submit():
        fac_data = {'num': form.number.data}
        result = requests.get(f'http://localhost:{port}/api/v2/math/factorization', data=fac_data).json()
        print(result)

        if result['success'] == 'OK':
            params['result'] = ', '.join([str(i) for i in result['result']])
        else:
            params['message'] = result['message']
        return render_template('factorization.html', **params)
    return render_template('factorization.html', **params)


@app.route('/factorial', methods=['GET', 'POST'])
def factorial_form():
    form = FactorizationForm()
    params = {'title': "Факториал", 'form': form}
    if form.validate_on_submit():
        fac_data = {'num': form.number.data}
        result = requests.get(f'http://localhost:{port}/api/v2/math/factorial', data=fac_data).json()
        if result['success'] == 'OK':
            params['result'] = result['result']
        else:
            params['message'] = result['message']
        return render_template('factorization.html', **params)
    return render_template('factorization.html', **params)


@app.route('/geometry')
def geometry():
    buttons = {'Посчитать площадь треугольника через стороны': 'geron'}
    return render_template('subject.html', title='webmate', sbj='Геометрия', btns=buttons)


@app.route('/geron', methods=['GET', 'POST'])
def geron_form():
    form = GeronForm()
    params = {'title': "Формула Герона", 'form': form}
    if form.validate_on_submit():
        geron_data = {'a': form.first_number.data, 'b': form.second_number.data, 'c': form.third_number.data}
        result = requests.get(f'http://localhost:{port}/api/v2/math/geron', data=geron_data).json()
        if result['success'] == 'OK':
            params['result'] = result['result']
        else:
            params['message'] = result['message']
        return render_template('geron.html', **params)
    return render_template('geron.html', **params)


@app.route('/informatics')
def informatics():
    buttons = {'Построить таблицу истинности': 'create_table',
               'Перевод между разными системами счисления': 'translate'}
    return render_template('subject.html', title='webmate', sbj='Информатика', btns=buttons)


@app.route('/create_table', methods=['GET', 'POST'])
def create_table_form():
    form = CreateTableForm()
    params = {'title': "Таблица истинности", 'form': form}
    if form.validate_on_submit():
        table_data = {'inpt': form.expression.data}
        result = requests.get(f'http://localhost:{port}/api/v2/inf/truth_table', data=table_data).json()
        if result['success'] == 'OK':
            params['header'] = result['header']
            params['result'] = result['result']
        else:
            params['message'] = result['message']
        return render_template('truth_table.html', **params)
    return render_template('truth_table.html', **params)


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    form = TranslateForm()
    params = {'title': "Таблица истинности", 'form': form}
    if form.validate_on_submit():
        translate_data = {'a': form.first_number.data, 'b': form.first_step.data, 'c': form.second_step.data}
        result = requests.get(f'http://localhost:{port}/api/v2/inf/traslate', data=translate_data).json()
        if result['success'] == 'OK':
            params['result'] = result['result']
        else:
            params['message'] = result['message']
        return render_template('translate.html', **params)
    return render_template('translate.html', **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    params = {'title': 'Вход',
              'form': form}
    if form.validate_on_submit():
        login_data = {'login': form.login.data,
                      'password': form.password.data}
        result = requests.post(f'http://localhost:{port}/api/v2/login', data=login_data).json()
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
        result = requests.post(f'http://localhost:{port}/api/v2/register', data=register_data).json()
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
    port = int(os.environ.get("PORT", 5000))
    print(port)
    app.run(port=port, host='0.0.0.0')
