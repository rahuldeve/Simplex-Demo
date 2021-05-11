import numpy as np
from scipy.spatial import HalfspaceIntersection, ConvexHull
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import io
import base64
import copy

from solve import generate_A, generate_b


def visualize(program, steps):
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
    points = np.around(hs.intersections, 3)
    points = points[:, :2]
    xlim = (-1, max([p[0] for p in points]) + 1)
    ylim = (-1, max([p[1] for p in points]) + 1)

    steps = np.array(steps)
    steps = steps[:, :2]


    figs = []
    for i, (p,q) in enumerate(steps):

        fig = plt.figure()
        ax = fig.add_subplot('111', aspect='equal')
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        x = np.linspace(*xlim, 100)

        # for h in halfspaces:
        #     if h[1]== 0:
        #         ax.axvline(-h[2]/h[0], color="#2c3e50")
        #     else:
        #         ax.plot(x, (-h[2]-h[0]*x)/h[1], color="#2c3e50")

        x, y = zip(*points)
        # points = list(zip(x, y))
        convex_hull = ConvexHull(points)
        polygon = Polygon([points[v] for v in convex_hull.vertices], color="#34495e")
        ax.add_patch(polygon)
        ax.plot(x, y, 'o', color="#e67e22")

        ax.plot(p, q, 'o')


        byarray = io.BytesIO()
        fig.savefig(byarray, format='png', bbox_inches="tight")
        b64 = base64.b64encode(byarray.getvalue()).decode("utf-8").replace("\n", "")
        b64 = 'data:image/png;base64,%s' % b64
        figs.append(b64)


    return figs