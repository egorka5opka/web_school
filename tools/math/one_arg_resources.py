from flask import jsonify
from flask_restful import reqparse, abort, Resource


parser = reqparse.RequestParser()
parser.add_argument('num', required=True, location='form', type=int)


class FactorizationRes(Resource):
    def get(self):
        args = parser.parse_args()
        num = args['num']
        primes = []
        if num < 0:
            primes.append(-1)
            num *= -1
        div = 2
        while div**2 <= num:
            while num % div == 0:
                num /= div
                primes.append(num)
            div += 1
        return jsonify({'success': 'OK',
                        'result': primes})


class FactorialRes(Resource):
    def get(self):
        args = parser.parse_args()
        num = args['num']
        if num < 0:
            return jsonify({'success': 'failed',
                            'message': 'Число должно быть неотрицательно'})
        factorial = 1
        for i in range(2, num + 1):
            factorial *= i
        return jsonify({'success': 'OK',
                        'message': factorial})
