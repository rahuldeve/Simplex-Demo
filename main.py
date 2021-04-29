from parse import *
from utils import *
from convert import *
from solve import *

text = '''
var x1 >= 0;
var x2 >= 0;

st:   x1 +   x2 <=  9;
st: 3x1 +   x2 <= 18;
st:   x1        <=  7;
st:          x2 >=  6;

maximize:     3x1 + 2x2;
'''

p = parse_linear_program(text)
q = to_standardard_form(p)
q = to_slack_form(q)
print(q.variables.keys())
print(simplex(q))