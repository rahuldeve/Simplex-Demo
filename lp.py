from utils import *
import math
from copy import deepcopy

def is_ineq_nonnegative(var_range):
    return var_range[0] < 0 and var_range[1] <= 0


def fix_non_negative_variable_constraints(program):
    to_replace = set([
        v.name for v in program.variables.values()
        if is_ineq_nonnegative(v.range)
    ])

    new_name_mapping = { old_name : old_name + '\'' for old_name in to_replace}

    # replace x with x'; set the appropriate variable range
    for v_name in to_replace:
        variable = program.variables[v_name]
        variable.name = new_name_mapping[v_name]
        variable.range = (0, math.inf)

        program.variables.pop(v_name, None)
        program.variables[new_name_mapping[v_name]] = variable

    # flip signs and inequality in constraints    
    for c in program.constraints:
        for idx in range(len(c.variable_names)):
            vi = c.variable_names[idx]
            if vi in to_replace :
                c.variable_names[idx] = new_name_mapping[vi]
                c.constants[idx] *= -1

    # flip signs in objective function
    for idx in range(len(program.objective_function.variable_names)):
        vi = program.objective_function.variable_names[idx]
        if vi in to_replace:
            program.objective_function.variable_names[idx] = new_name_mapping[vi]
            program.objective_function.constants[idx] *= -1

    return program


# Convert x + y >= 3 to -x + -y <= -3 
def fix_constraints_inequality_geq(program):
    for c in program.constraints:
        if c.ineq == Inequality.geq:
            c.constants = [-1*const for const in c.constants]
            c.ineq = c.ineq.flip()
            c.value *= -1

    return program


def fix_equality_in_constraint(program):

    has_equality = [
        i for i,c in enumerate(program.constraints)
        if c.ineq == Inequality.eq
    ]

    converted = []
    # convert x + y = 1 to x + y <= 1 and x + y >= 1
    for idx, c in enumerate(program.constraints):
        if c.ineq == Inequality.eq:
            # convert to <=
            c.ineq = Inequality.leq
            # convert to >=
            cn = deepcopy(c)
            cn.ineq = Inequality.geq

            converted.append(c)
            converted.append(cn)

        else:
            converted.append(c)
    
    program.constraints = converted
    return program

    
def standardize(program):
    program = fix_non_negative_variable_constraints(program)
    program = fix_constraints_rhs_negative(program)
    # Handle unbound variables
    # Handle equality signs
    return program