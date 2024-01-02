#from TSP_Model import Model
from local_search import *

m = Model()
m.BuildModel()
s = local_search(m)
sol = s.solve()





