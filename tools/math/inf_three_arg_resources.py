from flask import jsonify
from flask_restful import reqparse, abort, Resource
from math import sqrt

parser = reqparse.RequestParser()
parser.add_argument('a', required=True, location='form', type=str)
parser.add_argument('b', required=True, location='form', type=int)
parser.add_argument('c', required=True, location='form', type=int)


class Translation(Resource):
    def get(self):
        args = parser.parse_args()
        a = args['a']
        b = args['b']
        c = args['c']
        if a[0] == '-':
            return jsonify({'success': 'failed',
                            'message': 'Число отрицательное'})
        if b > 36 or c > 36 or b < 2 or c < 2:
            return jsonify({'success': 'failed',
                            'message': 'Основание системы счисления это число от 2 до 36'})
        try:
            a_int = int(a, b)
        except ValueError:
            return jsonify({'success': 'failed',
                            'message': 'Невалидное число'})
        ans = list()
        alfa = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        while a_int > 0:
            ans.append(alfa[a_int % c])
            a_int //= c
        ans.reverse()
        return jsonify({'success': 'OK',
                        'result': ''.join(ans)})
