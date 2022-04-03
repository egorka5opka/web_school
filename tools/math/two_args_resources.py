from flask import jsonify
from flask_restful import reqparse, abort, Resource


parser = reqparse.RequestParser()
parser.add_argument('a', required=True, location='form', type=int)
parser.add_argument('b', required=True, location='form', type=int)


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


class GCDRes(Resource):
    def get(self):
        args = parser.parse_args()
        a, b = args['a'], args['b']
        if a < 0 or b < 0:
            return jsonify({'success': 'failed',
                            'message': 'Числа должны быть неотрицательны'})
        return jsonify({'success': 'OK',
                        'result': gcd(a, b)})


class LCMRes(Resource):
    def get(self):
        args = parser.parse_args()
        a, b = args['a'], args['b']
        if a < 0 or b < 0:
            return jsonify({'success': 'failed',
                            'message': 'Числа должны быть неотрицательны'})
        d = gcd(a, b)
        return jsonify({'success': 'OK',
                        'result': a / d * b})
