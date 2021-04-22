from utils import *

def is_ineq_nonnegative(ineq, value):
    # checking only for the following case below
    # check x < 0 or x <= 0
    return ineq == Inequality.leq and value <= 0


def fix_non_negative_variable_constraints(program):
    to_fix = set([v for v in program.variables if is_ineq_nonnegative(v.ineq, v.value)])

    # flip signs and inequality in constraints    
    for c in program.constraints:
        for idx in range(len(c.variables)):
            vi = c.variables[idx]
            if vi in to_fix :
                c.constants[idx] *= -1

    # flip signs in objective function
    for idx in range(len(program.objective_function.variables)):
        vi = program.objective_function.variables[idx]
        if vi in to_fix:
            program.objective_function.constants[idx] *= -1

    return program


def fix_constraints_rhs_negative(program):
    for c in program.constraints:
        if c.value < 0:
            c.constants = [-1*const for const in c.constants]
            c.ineq = c.ineq.flip()
            c.value *= -1

    return program


def standardize(program):
    program = fix_constraints_rhs_negative(program)
    program = fix_constraints_rhs_negative(program)
    # Handle unbound variables
    # Handle equality signs
    return program