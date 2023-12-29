import random
import math

class Node:
    def __init__(self, idd, xx, yy, dem):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.demand = dem
        self.isRouted = False

class Route:
    def __init__(self, dp, cap, empty_vehicle_weight):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.empty_vehicle_weight = empty_vehicle_weight
        self.load = 0

class Model:
# instance variables
    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.capacity = -1
        self.empty_vehicle_weight = -1
        self.tot_customers = -1

    def BuildModel(self):
        file_name='Instance.txt'
        all_lines = list(open(file_name, "r"))
        separator = ','

        line_counter = 0

        ln = all_lines[line_counter]
        no_spaces = ln.split(sep=separator)
        self.capacity = int(no_spaces[1])   #8

        line_counter += 1
        ln = all_lines[line_counter]
        no_spaces = ln.split(sep=separator)
        self.empty_vehicle_weight = int(no_spaces[1])   #6

        line_counter += 1
        ln = all_lines[line_counter]
        no_spaces = ln.split(sep=separator)
        self.tot_customers = int(no_spaces[1])  #250

        line_counter += 3
        ln = all_lines[line_counter]

        #create node depot me idd=0 xx=20 yy=20 dem=0
        no_spaces = ln.split(sep=separator)
        x = float(no_spaces[1])
        y = float(no_spaces[2])
        depot = Node(0, x, y, 0)
        
        #add it as first element at allNodes list
        self.allNodes.append(depot)
        
        #i apo 0 ews 249, ginetai 250 fores synolika h dhmiourgia Node kai h prosthiki sto allNodes kai sto customers
        #h lista allNodes ksekinaei me depot ara exei 251 stoixeia enw customers exei akribws 250 stoixeia xwris depot mesa
        for i in range(self.tot_customers):
            line_counter += 1
            ln = all_lines[line_counter]
            no_spaces = ln.split(sep=separator)
            id = int(no_spaces[0])
            x = float(no_spaces[1])
            y = float(no_spaces[2])
            demand = float(no_spaces[3])
            cust = Node(id, x, y, demand)
            self.allNodes.append(cust)
            self.customers.append(cust)
          
        #rows=251, 250 customers + 1 depot
        rows = len(self.allNodes)
        #pinakas 250X250
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        #kataskeyh pinaka km apo kombo se kombo basei typou eukleidias apostashs
        for i in range(rows):
            a = self.allNodes[i]
            for j in range(rows):
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.matrix[i][j] = dist
        for i in range(rows):
            self.matrix[i][0]=0.0
        #print(self.matrix[0][250])

#m = Model()
#m.BuildModel()