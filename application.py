from flask import Flask, render_template, request, jsonify

from parse import *
from utils import *
from convert import *
from solve import *
from explore import *


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/results', methods=['get', 'post'])
def results():
    inp = request.args.get('input')
    print(inp)

    p = parse_linear_program(inp)
    p = to_standardard_form(p)
    p = to_slack_form(p)

    try:
        final, points, tableau_steps, explanations = simplex(p)
    except Exception as e:
        # print('-------', str(e))
        return str(e), 500

    figures = visualize(p, points)

    steps = []
    for point, fig, tab_step, exp in zip(points, figures, tableau_steps, explanations):
        
        tab_row, tab_col, tab = tab_step

        step = {}
        step['point'] = point
        step['figure'] = fig
        step['matrix'] = {
            'title_columns' : tab_col,
            'title_rows' : tab_row,
            'data': tab.tolist(),
            'explanations': exp
        }

        # print(point)
        steps.append(step)


    return jsonify({'iteration_steps': steps})

if __name__ == '__main__':
    app.run(debug=True)