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
    inp = request.form['input']

    p = parse_linear_program(inp)
    q = to_standardard_form(p)
    q.intersection_points = get_all_intersection_points(q)
    q = to_slack_form(q)

    intersection_points = q.intersection_points
    final, steps = simplex(q)

    ret = {
        'intersection_points' : intersection_points,
        'simplex_iteration_steps': steps,
        'optimal_point': final
    }

    return jsonify(ret)

if __name__ == '__main__':
    app.run(debug=True)