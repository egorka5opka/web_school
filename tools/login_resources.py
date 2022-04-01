from flask import jsonify
from flask_restful import reqparse, abort, Resource
from data.db_session import create_session
from data.users import User


parser = reqparse.RequestParser()
parser.add_argument('login', required=True, type=str)
parser.add_argument('password', required=True, type=str)


class RegisterRes(Resource):
    def post(self):
        args = parser.parse_args()
        login = args['login']
        if not login.isalnum():
            return jsonify({'success': 'failed',
                            'message': 'Логин должен состоять из букв и цифр'})
        session = create_session()
        search_login = session.query(User).filter(User.login == args['login']).first()
        if search_login:
            return jsonify({'success': 'failed',
                            'message': 'Логин занят'})
        password = args['password']
        if len(password) < 5:
            return jsonify({'success': 'failed'},
                           'message:' 'Пароль слишком короткий')
        user = User(login=login,
                    password=password)
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK', 'user': user.to_dict(only=('id', 'login'))})


class LoginRes(Resource):
    def post(self):
        args = parser.parse_args()
        session = create_session()
        user = session.query(User).filter(User.login == args['login']).first()
        if not user:
            return jsonify({'success': 'failed',
                            'message': 'Введены неверные данные',
                            'comment': 'No user with this login'})
        if not user.check_password(args['password']):
            return jsonify({'success': 'failed',
                            'message': 'Введены неверные данные',
                            'comment': 'Wrong password'})
        return jsonify({'success': 'OK',
                        'user': user.to_dict(only=('id', 'login'))})
