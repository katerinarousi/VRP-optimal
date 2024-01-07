from Solver import *
from VND import *

m = Model()
m.BuildModel()
s = Solver(m)
initial_solution = s.solve()
s1 = SolverVND(m, initial_solution)
print("ok")
final_solution = s1.solve()
