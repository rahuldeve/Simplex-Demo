from parse import parse_linear_program
from lp import standardize

text = '''
var x1 >= 0;
var x2 <= 0;

st:   x1 +   x2 <=  9;
st: 3x1 +   x2 <= 18;
st:   x1        <=  7;
st:          x2 >=  6;

maximize:     3x1 + 2x2;
'''

prog = parse_linear_program(text)