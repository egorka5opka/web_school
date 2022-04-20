from flask import jsonify
from flask_restful import reqparse, abort, Resource
from itertools import permutations

parser = reqparse.RequestParser()
parser.add_argument('inpt', required=True, location='form', type=str)


class TruthTable(Resource):
    def get(self):
        args = parser.parse_args()
        expression = args['inpt']
        expression_new = ''
        for_operations = {'&': 'and', '|': 'or', '!': 'not', '^': '!=', '=': '==', '-': '<=', ' ': ' '}
        keys = list(for_operations.keys())
        param = list()
        index = 0
        i = 0
        while i < len(expression):
            if expression[i].isalpha():
                expression_new += '{' + str(index) + '}'
                index += 1
                param.append(expression[i])
            else:
                if expression[i] not in keys:
                    jsonify({'success': 'failed',
                             'message': 'Невалидный символ'})
                else:
                    expression_new += for_operations[expression[i]]
                    if expression[i] in ['=', '-']:
                        i += 1
            i += 1
        permut = [0 for i in range(index)] + [1 for i in range(index)]
        all_permutations = sorted(list(set(permutations(permut, index))))
        param.append(expression)
        results = list()
        for elem in all_permutations:
            new_str = expression_new.format(*elem)
            small_ans = list(elem)
            small_ans.append(int(eval(new_str)))
            results.append(small_ans)
        return jsonify({'success': 'OK',
                        'header': param,
                        'result': results})
