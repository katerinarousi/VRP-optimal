from Solver import *
from combined import *
from SolutionDrawer import *


m = Model()
m.BuildModel()
s = Solver(m)
initial_solution = s.solve()

opt = SolverCom(m, initial_solution)
opt.solve()
