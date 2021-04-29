import math
import numpy as np

# reference: https://geekrodion.com/blog/operations/simplex
# https://github.com/RodionChachura/optimization/blob/master/linear_programming.ipynb


def generate_A(program, variable_names_to_idx):
    A = []
    N = len(program.variables)

    for c in program.constraints:
        row = [0 for _ in program.variables.keys()]
        # row = np.zeros(N)
        for name, constant in zip(c.variable_names, c.constants):
            idx = variable_names_to_idx[name]
            row[idx] = constant

        A.append(row)

    return A
    
    
def generate_b(program):
    b = [c.value for c in program.constraints]
    return b


def generate_c(program, variable_names_to_idx):
    # c = np.zeros(len(program.variables))
    c = [0 for _ in program.variables.keys()]
    obj = program.objective_function
    for name, constant in zip(obj.variable_names, obj.constants):
        idx = variable_names_to_idx[name]
        c[idx] = constant

    return c


def to_tableau(program):
    variable_names_to_idx = {v : i for i,v in enumerate(program.variables.keys())}

    A = generate_A(program, variable_names_to_idx)
    b = generate_b(program)
    c = generate_c(program, variable_names_to_idx)

    xb = [eq + [x] for eq, x in zip(A, b)]
    z = c + [0]
    return xb + [z]


def can_be_improved(tableau):
    z = tableau[-1]
    return any(x > 0 for x in z[:-1])


def get_pivot_position(tableau):
    z = tableau[-1]
    column = next(i for i, x in enumerate(z[:-1]) if x > 0)
    
    restrictions = []
    for eq in tableau[:-1]:
        el = eq[column]
        restrictions.append(math.inf if el <= 0 else eq[-1] / el)

    row = restrictions.index(min(restrictions))
    return row, column


def pivot_step(tableau, pivot_position):
    new_tableau = [[] for eq in tableau]
    
    i, j = pivot_position
    pivot_value = tableau[i][j]
    new_tableau[i] = np.array(tableau[i]) / pivot_value
    
    for eq_i, eq in enumerate(tableau):
        if eq_i != i:
            multiplier = np.array(new_tableau[i]) * tableau[eq_i][j]
            new_tableau[eq_i] = np.array(tableau[eq_i]) - multiplier
   
    return new_tableau


def is_basic(column):
    return sum(column) == 1 and len([c for c in column if c == 0]) == len(column) - 1


def get_solution(tableau):
    columns = np.array(tableau).T
    solutions = []
    for column in columns[:-1]:
        solution = 0
        if is_basic(column):
            one_index = column.tolist().index(1)
            solution = columns[-1][one_index]
        solutions.append(solution)
        
    return solutions


def simplex(program):
    tableau = to_tableau(program)

    while can_be_improved(tableau):
        pivot_position = get_pivot_position(tableau)
        tableau = pivot_step(tableau, pivot_position)

    return get_solution(tableau)
