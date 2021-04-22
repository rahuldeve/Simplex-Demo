from utils import *
from pyparsing import *
import math

def handle_inequality(tokens):
    mapping = {
        # '<' : Inequality.l,
        # '>' : Inequality.g,
        '<=': Inequality.leq,
        '>=': Inequality.geq,
        '=' : Inequality.eq
    }
    token = tokens[0]
    return mapping[token]


def handle_operation(tokens):
    mapping = {
        '+' : Operation.add,
        '-' : Operation.sub,
        # '*' : Operation.mul,
        # '/' : Operation.div
    }

    token = tokens[0]
    return mapping[token]


def handle_variable_with_constant(tokens):
    if len(tokens) == 1:
        # The tokens[0] object will be of type Variable since it was already parsed before
        return (1, tokens[0])
    else:
        # The tokens[1] object will be of type Variable since it was already parsed before
        return (tokens[0], tokens[1])



#################################################################################################
#
# Basic parsers
#
#################################################################################################

## Parses any number to floats
number = pyparsing_common.fnumber
## Parses any string as a variable object
var = Regex(r'[a-zA-Z]+[0-9]*')
## Parses '3x' as [3, Variable(x)]
var_with_constant = var | Optional(number) + var
# Automatically put the variable and its constants in a tuple; Easier to process later
var_with_constant.setParseAction(handle_variable_with_constant)
## Parses any inequality symbols (<=, >=, =) to an object representation
ineq = Regex(r'[<>]?=').setParseAction(handle_inequality)
## Parses +, -, *, / to an object representation
oper = oneOf('+ -').setParseAction(handle_operation)
end_of_line = Literal(';').suppress()



#################################################################################################
#
# Variable declaration parser
#
#################################################################################################

def construct_variable(parsed):
    constant, var_name = parsed[0]
    ineq = parsed[1]
    value = parsed[2]

    # Assume variable declaration can only have 0 in RHS
    assert value == 0
    # Equality constraint not supported in variable declaration
    assert ineq == Inequality.leq or ineq == Inequality.geq

    var_range = (-math.inf, math.inf)
    if ineq == Inequality.leq:
        var_range = (-math.inf, value)
    elif ineq == Inequality.geq:
        var_range = (value, math.inf)

    return Variable(var_name, var_range)

var_decl = Literal('var ').suppress() + var_with_constant + ineq + number + end_of_line
var_decl.setParseAction(construct_variable)



#################################################################################################
#
# Constraint declaration parser
#
#################################################################################################

def construct_constraint(parsed):
    value = parsed[-1]
    ineq = parsed[-2]

    expression = parsed[:-2]
    variable_names = []
    constants = []

    constant, v_name = expression[0]
    variable_names.append(v_name)
    constants.append(constant)
    expression = expression[1:]

    assert len(expression) % 2 == 0
    for idx in range(0, len(expression), 2):
        assert type(expression[idx]) == Operation
        assert type(expression[idx + 1]) == tuple

        op = expression[idx]
        constant, v_name = expression[idx + 1]

        if op == Operation.sub:
            constant = -1 * constant

        variable_names.append(v_name)
        constants.append(constant)

    return Constraint(variable_names, constants, ineq, value)

st_literal = Literal('st: ').suppress()
expr = var_with_constant + ZeroOrMore(oper + var_with_constant)
constraint_decl = st_literal + expr + ineq + number + end_of_line
constraint_decl.setParseAction(construct_constraint)



#################################################################################################
#
# Objective declaration parser
#
#################################################################################################

def construct_objective(parsed):
    assert type(parsed[0]) == ObjectiveTypes
    obj_type = parsed[0]
    function_expr = parsed[1:]

    variable_names = []
    constants = []

    constant, v_name = function_expr[0]
    variable_names.append(v_name)
    constants.append(constant)
    function_expr = function_expr[1:]

    assert len(function_expr) % 2 == 0
    for idx in range(0, len(function_expr), 2):
        assert type(function_expr[idx]) == Operation
        assert type(function_expr[idx + 1]) == tuple

        op = function_expr[idx]
        constant, v_name = function_expr[idx + 1]

        if op == Operation.sub:
            constant = -1 * constant

        variable_names.append(v_name)
        constants.append(constant)

    return Objective(obj_type, variable_names, constants)

maximize = Literal('maximize').setParseAction(lambda x: ObjectiveTypes.maximize)
minimize = Literal('minimize').setParseAction(lambda x: ObjectiveTypes.minimize)
lin_type = maximize | minimize
objective_decl = lin_type + Literal(': ').suppress() + expr + end_of_line
objective_decl.setParseAction(construct_objective)



#################################################################################################
#
# Linear program parser
#
#################################################################################################

variables = OneOrMore(var_decl).setParseAction(lambda toks: [toks])
constraints = OneOrMore(constraint_decl).setParseAction(lambda toks: [toks])
program_decl = variables + constraints + objective_decl


def parse_linear_program(text):
    res = program_decl.parseString(text)
    variables = list(res[0])
    constraints = list(res[1])
    objective_func = res[2]

    program = Program(variables, constraints, objective_func)
    return program