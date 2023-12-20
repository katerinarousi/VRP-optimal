import random
import math


class Model:

# instance variables
    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.capacity = -1

    def BuildModel(self):
        random.seed(1)

        file_path = 'Instance.txt'
        with open(file_path, 'r') as file:
            lines = file.readlines()

# setting depot - storage
        values = lines[5].strip().split(',')
        id_val = int(values[0])
        xcoord = int(values[1])
        ycoord = int(values[2])
        demand = float(values[3])
        depot = Node(id_val, xcoord, ycoord, demand)
        self.allNodes.append(depot)

# setting capacity
        values = lines[0].strip().split(',')
        self.capacity = int(values[1])

# setting customers
        values = lines[2].strip().split(',')
        totalCustomers = int(values[1])

        for line in lines[6:]:
            values = line.strip().split(',')

            id_val = int(values[0])
            xcoord = int(values[1])
            ycoord = int(values[2])
            demand = float(values[3])

            cust = Node(id_val, xcoord, ycoord, demand)
            self.allNodes.append(cust)
            self.customers.append(cust)

        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

# Needs to be fixed
        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.matrix[i][j] = dist

class Node:
    def __init__(self, idd, xx, yy, dem):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.demand = dem
        self.isRouted = False

class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.load = 0