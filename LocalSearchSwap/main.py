from Solver import *
from Relocation_Solver import *
from Swap_Solver import *

m = Model()
m.BuildModel()
s = Solver(m)
initial_solution = s.solve()

s1 = Solver2(m, initial_solution)
s1.solve()
