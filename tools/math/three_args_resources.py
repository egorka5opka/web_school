from flask import jsonify
from flask_restful import reqparse, abort, Resource
from math import sqrt


parser = reqparse.RequestParser()
parser.add_argument('a', required=True, location='form', type=float)
parser.add_argument('b', required=True, location='form', type=float)
parser.add_argument('c', required=True, location='form', type=float)


class GeronRes(Resource):
    def get(self):
        args = parser.parse_args()
        a = args['a']
        b = args['b']
        c = args['c']
        if max(a, b, c) >= (a + b + c - max(a, b, c)):
            return jsonify({'success': 'failed',
                            'message': 'Это не стороны треугольника'})
        half = (a + b + c) / 2
        square = sqrt(half * (half - a) * (half - b) * (half - c))
        return jsonify({'success': 'OK',
                        'result': square})
