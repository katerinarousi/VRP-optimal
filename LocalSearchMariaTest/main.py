from Solver import *
from Relocation_Solver import *

m = Model()
m.BuildModel()
s = Solver(m)
initial_solution = s.solve()
print("YESSIR")
s1 = Solver1(m, initial_solution)
s1.solve()