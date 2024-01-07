from Solver import *
from Relocation_Solver import *
from Swap_Solver import *
from TwoOpt_Solver import *

m = Model()
m.BuildModel()
s = Solver(m)
initial_solution = s.solve()
s1 = Solver3(m,initial_solution)
first_good = s1.solve()
s2 = Solver1(m, first_good)
second_good = s2.solve()
s3 = Solver2(m ,second_good )
third_good = s3.solve()