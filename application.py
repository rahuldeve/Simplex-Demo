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
    p = to_standardard_form(p)
    p.intersection_points = get_all_intersection_points(p)
    p = to_slack_form(p)

    intersection_points = p.intersection_points
    final, steps = simplex(p)

    return render_template('results.html', program=p)

if __name__ == '__main__':
    app.run(debug=True)