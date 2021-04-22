from enum import Enum
from dataclasses import dataclass, field
from typing import List

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
    ineq: Inequality
    value: float

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        return (self.name, self.ineq.value, self.value).__repr__()



@dataclass
class Constraint():
    variables: List
    constants: List
    ineq: Inequality
    value: float


class ObjectiveTypes(Enum):
    maximize = 1
    minimize = 2


@dataclass
class Objective():
    obj_type: ObjectiveTypes
    variables: List
    constants: List


class Program():
    variables: List[Variable]
    constraints: List[Constraint]
    objective_function: Objective

    def __init__(self, variables, constraints, objective_function):
        self.variables = variables
        self.constraints = constraints
        self.objective_function = objective_function

        # Map variable_names to variables in constraints and objective_function
        # Handle case for unbound variables. They might not have been declared
        
        mapping = {v.name : v for v in variables}
        for c in self.constraints:
            c.variables = [mapping[v_name] for v_name in c.variables]

        self.objective_function.variables = [
            mapping[v_name] for v_name in self.objective_function.variables
        ]