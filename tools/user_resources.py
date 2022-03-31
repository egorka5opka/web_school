from flask import jsonify
from flask_restful import reqparse, abort, Resource
from data.db_session import create_session
from data.users import User


parser = reqparse.RequestParser()
parser.add_argument('login', required=True, type=str)
parser.add_argument('password', required=True, type=str)


class UserResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = create_session()
        user = User(login=args['login'],
                    password=args['password'])
        search_login = session.query(User).filter(User.login == args['login']).fetchone()
        if search_login:
            return jsonify({'success': 'failed',
                            'message': 'Логин занят'})
        session.add(User)
        session.commit()
        return jsonify({'success': 'OK'})
