from parse import *
from utils import *
from convert import *
from solve import *
from explore import *

text = '''
var x1>=0;
var x2>=0;

st: x1>=3;
st: x2>=6;

maximize: x1+x2;
'''

p = parse_linear_program(text)
q = to_standardard_form(p)
# q.intersection_points = get_all_intersection_points(q)
q = to_slack_form(q)
# print(q.intersection_points)
final, steps, _ = simplex(q)
# print('simplex steps', steps)
print('final', final)
print(steps)