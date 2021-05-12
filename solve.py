import math
import numpy as np
import copy
from flask import render_template


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

    program.steps['mat_A'] = np.array(A)
    return A


def generate_b(program):
    b = [c.value for c in program.constraints]
    program.steps['mat_b'] = np.array(b)
    return b


def generate_c(program, variable_names_to_idx):
    # c = np.zeros(len(program.variables))
    c = [0 for _ in program.variables.keys()]
    obj = program.objective_function
    for name, constant in zip(obj.variable_names, obj.constants):
        idx = variable_names_to_idx[name]
        c[idx] = constant

    program.steps['mat_c'] = np.array(c)
    return c


def to_tableau(program):
    variable_names_to_idx = {v: i for i, v in enumerate(program.variables.keys())}

    A = generate_A(program, variable_names_to_idx)
    b = generate_b(program)
    c = generate_c(program, variable_names_to_idx)

    xb = [eq + [x] for eq, x in zip(A, b)]
    z = c + [0]
    tableu = xb + [z]

    program.steps['initial_tableu'] = np.array(tableu)
    return tableu


def is_non_optimal(tableau):
    z = tableau[-1]
    return any(x > 0 for x in z[:-1])


def get_pivot_position(tableau):
    explanations = []
    z = tableau[-1]
    column = next(i for i, x in enumerate(z[:-1]) if x > 0)

    # explanations.append(f'''Take the last row of the tableau and check for the first instance of a number > 0.
    # In this iteration, the {column}th row of the has the first instance of a positive number > 0.
    # Note that if no such element exists, then the linear program is unbounded and the simplex algorithm will stop''')

    restrictions = []
    for eq in tableau[:-1]:
        el = eq[column]
        restrictions.append(math.inf if el <= 0 else eq[-1] / el)

    if all([r == math.inf for r in restrictions]):
        raise Exception("Linear program is unbounded.")

    row = restrictions.index(min(restrictions))

    explanations = render_template('pivot_pos_expl.html', row=row, column=column, restrictions=restrictions,
                                   prev_tab=np.array(tableau))

    return (row, column), explanations


def pivot_step(tableau, pivot_position):
    new_tableau = [[] for eq in tableau]

    i, j = pivot_position
    pivot_value = tableau[i][j]
    new_tableau[i] = np.array(tableau[i]) / pivot_value

    for eq_i, eq in enumerate(tableau):
        if eq_i != i:
            multiplier = np.array(new_tableau[i]) * tableau[eq_i][j]
            new_tableau[eq_i] = np.array(tableau[eq_i]) - multiplier

    explanations = render_template('pivot_step_expl.html', i=i, j=j, new_tableau=new_tableau)
    return new_tableau, explanations


def is_basic(column):
    return sum(column) == 1 and len([c for c in column if c == 0]) == len(column) - 1


def get_solution(tableau, program):
    columns = np.array(tableau).T
    solutions = []
    for column in columns[:-1]:
        solution = 0
        if is_basic(column):
            one_index = column.tolist().index(1)
            solution = columns[-1][one_index]
        solutions.append(solution)

    solution_map = {name: val for name, val in zip(program.variables.keys(), solutions)}
    explanations = render_template('sol_extract_expl.html', transposed_tab=columns, solution_map=solution_map)
    return solutions, explanations


def simplex(program):
    tableau = to_tableau(program)

    first_sol, first_sol_expl = get_solution(tableau, program)
    explored_points = [first_sol[:2]]
    tableau_list = [np.array(tableau)]
    explanations = [render_template('first_step_expl.html', program=program, 
    is_non_optimal = is_non_optimal(tableau), first_sol=first_sol[:2])]

    variable_names_to_idx = {v: i for i, v in enumerate(program.variables.keys())}
    idx_to_variable_name = [name for name in program.variables.keys()]

    curr_tab_row_titles = [v.name for v in program.variables.values() if v.is_slack]
    curr_tab_col_titles = list(program.variables.keys())

    tab_row_titles = [copy.deepcopy(curr_tab_row_titles)]
    tab_col_titles = [copy.deepcopy(curr_tab_col_titles)]
    while is_non_optimal(tableau):
        iteration_steps = {}
        pivot_position, piv_pos_expl = get_pivot_position(tableau)
        tableau, new_tab_expl = pivot_step(tableau, pivot_position)
        sol, sol_expl = get_solution(tableau, program)
        explored_points.append(sol[:2])

        piv_row, piv_col = pivot_position
        col_var = curr_tab_col_titles[piv_col]
        row_var = curr_tab_row_titles[piv_row]

        curr_tab_col_titles[piv_col] = row_var
        curr_tab_row_titles[piv_row] = col_var

        np_tab = np.array(tableau)
        np_tab = np.around(np_tab, 3)
        tableau_list.append(np_tab)
        tab_row_titles.append(copy.deepcopy(curr_tab_row_titles))
        tab_col_titles.append(copy.deepcopy(curr_tab_col_titles))

        step_expl = render_template('simplex_iter_expl.html',
                                    piv_pos_expl=piv_pos_expl, new_tab_expl=new_tab_expl, sol_expl=sol_expl,
                                    is_non_optimal=is_non_optimal(tableau))
        explanations.append(step_expl)

    final_sol = explored_points[-1]
    tableau_steps = list(zip(tab_row_titles, tab_col_titles, tableau_list))
    return final_sol, explored_points, tableau_steps, explanations
