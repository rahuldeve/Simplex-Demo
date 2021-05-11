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

    final, points, tableau_steps = simplex(p)

    figures = visualize(p, points)

    steps = []
    for point, fig, tab_step in zip(points, figures, tableau_steps):
        
        tab_row, tab_col, tab = tab_step

        step = {}
        step['point'] = point
        step['figure'] = fig
        step['matrix'] = {
            'title_columns' : tab_col,
            'title_rows' : tab_row,
            'data': tab.tolist()
        }

        # print(point)
        steps.append(step)


    # return render_template('results.html', program=p)
    # print(steps)
    # return render_template('test.html', steps=steps)
    return jsonify({'iteration_steps': steps})

if __name__ == '__main__':
    app.run(debug=True)