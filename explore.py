import numpy as np
from scipy.spatial import HalfspaceIntersection
from scipy.optimize import linprog

from solve import generate_A, generate_b


def get_all_intersection_points(program):
    variable_names_to_idx = {v : i for i,v in enumerate(program.variables.keys())}
    A_ub = np.array(generate_A(program, variable_names_to_idx))
    b_ub = np.array(generate_b(program))

    res = linprog(method='interior-point', c=np.zeros(A_ub.shape[1]), A_ub=A_ub, b_ub=b_ub)
    feasible_point = res.x

    b_ub = np.expand_dims(-1*b_ub, 1)
    halfspaces = np.hstack((A_ub, b_ub))

    N = len(program.variables)
    shape = (N, N + 1)
    v_mat = np.zeros(shape)
    for idx in range(N):
        v_mat[idx, idx] = -1
    halfspaces = np.vstack((halfspaces, v_mat))

    hs = HalfspaceIntersection(halfspaces, feasible_point)
    return np.around(hs.intersections, 3).tolist()