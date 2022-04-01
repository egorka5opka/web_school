from flask import jsonify
from flask_restful import reqparse, abort, Resource
from data.db_session import create_session
from data.users import User


class UserRes(Resource):
    def get(self, user_id):
        return "dude"

