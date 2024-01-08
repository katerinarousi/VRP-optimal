from VND import *

m = Model()
m.BuildModel()

s = Clarke_n_Wright(m)
initial_solution = s.solve()

s1 = VND(m, initial_solution)
final_solution = s1.solve()