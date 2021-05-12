from flask import Flask, request, jsonify

from convert import *
from explore import *
from parse import *
from solve import *

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/results', methods=['get', 'post'])
def results():
    inp = request.args.get('input')

    p = parse_linear_program(inp)
    p = to_standardard_form(p)
    p = to_slack_form(p)

    try:
        final, points, tableau_steps, explanations = simplex(p)
    except Exception as e:
        return str(e), 500

    figures = visualize(p, points)

    steps = []
    for point, fig, tab_step, exp in zip(points, figures, tableau_steps, explanations):
        tab_row, tab_col, tab = tab_step

        step = {'point': point, 'figure': fig, 'matrix': {
            'title_columns': tab_col,
            'title_rows': tab_row,
            'data': tab.tolist(),
            'explanations': exp
        }}

        steps.append(step)

    return jsonify({'iteration_steps': steps})


if __name__ == '__main__':
    app.run(debug=True)
