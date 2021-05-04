from enum import Enum
from dataclasses import dataclass, field
from typing import List, Mapping

class Inequality(Enum):
    # l = '<'
    # g = '>'
    eq = '='
    leq = '<='
    geq = '>='

    def flip(self):
        mapping = {
            # Inequality.l : Inequality.g,
            # Inequality.g : Inequality.l,
            Inequality.leq : Inequality.geq,
            Inequality.geq : Inequality.leq,
        }

        return mapping[self]


class Operation(Enum):
    add = 1
    sub = 2
    # mul = 3
    # div = 4


@dataclass
class Variable():
    name: str
    range: (float, float)
    is_slack: bool = False

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        ret = f'{self.name} in {self.range}'
        if self.is_slack:
            ret = ret + f'\t\t[[slack]]'
        return ret



@dataclass
class Constraint():
    variable_names: List[str]
    constants: List[float]
    ineq: Inequality
    value: float

    def __repr__(self):
        zipped = zip(self.constants, self.variable_names)
        var_with_constants = [str(c)+v for c,v in zipped]
        lhs = ' + '.join(var_with_constants)
        return f'{lhs} {self.ineq.value} {self.value}'



class ObjectiveTypes(Enum):
    maximize = 1
    minimize = 2


@dataclass
class Objective():
    obj_type: ObjectiveTypes
    variable_names: List[str]
    constants: List[float]


@dataclass
class Program():
    def __init__(self, variables, constraints, objective_function):
        self.variables = {v.name : v for v in variables}
        self.constraints = constraints
        self.objective_function = objective_function

        self.explanations = []
        self.intersection_points = []


    def __repr__(self):

        # print variables:
        variables = []
        for v in self.variables.values():
            variables.append(f'var {v.name} in {v.range}')

        variables = '\n'.join(variables)

        # print constraints
        constraints = []
        for c in self.constraints:
            constraints.append(c.__repr__())

        constraints = '\n'.join(constraints)

        return variables + '\n\n' + constraints