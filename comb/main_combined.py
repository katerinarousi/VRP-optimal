from Solver import *
from comb.combined import *

m = Model()
m.BuildModel()
s = Solver(m)
initial_solution = s.solve()

s1 = SolverCom(m, initial_solution)
s1.solve()
