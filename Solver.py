from VRP_Model import *
#from SolutionDrawer import *

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []

class Saving:
    def __init__(self, n1, n2, sav):
        self.n1 = n1
        self.n2 = n2
        self.score = sav

class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.empty_vehicle_weight = m.empty_vehicle_weight
        self.sol = None
        self.bestSolution = None

    def solve(self):
        self.Clarke_n_Wright()
        self.RemoveLastDepot(self.sol)
        self.ReportSolution(self.sol)
        self.ReportToFile(self.sol, "example_solution.txt")
        return self.sol
    
    def RemoveLastDepot(self,sol):
        for i in range(len(sol.routes)):
            rt = sol.routes[i]
            rt.sequenceOfNodes.pop()
                
    def ReportSolution(self, sol):
        for i in range(len(sol.routes)):
            rt = sol.routes[i]
            for j in range (len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print(rt.cost)
        #SolDrawer.draw('MinIns', self.sol, self.allNodes)
        print(self.sol.cost)

    def ReportToFile(self, sol, filename):
        with open(filename, 'w') as f:
            f.write('Cost: \n' + str(self.sol.cost) + '\n')
            f.write('Routes: \n')
            f.write(str(len(sol.routes)) + '\n')
            for i in range(0,len(sol.routes)):
                rt = sol.routes[i]
                for j in range(0, len(rt.sequenceOfNodes)):
                    f.write(str(rt.sequenceOfNodes[j].ID))
                    if (j < len(rt.sequenceOfNodes)-1):
                        f.write(',')
                f.write('\n')

    def CalculateTotalCost(self, sol):
        sol.cost = 0.0
        for i in range(len(sol.routes)):
            rt = sol.routes[i] 
            self.UpdateRouteCostAndLoad(rt)
            sol.cost += rt.cost
        return sol.cost


    def UpdateRouteCostAndLoad(self, rt: Route):
        td = sum(n.demand for n in rt.sequenceOfNodes) #total demand of rt route
        tl = self.empty_vehicle_weight + td 
        tn_km = 0
        for i in range(len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i+1]
            tn_km += self.distanceMatrix[A.ID][B.ID] * tl
            tl -= B.demand  #helps to the calculation of tn_km
        
        rt.load = self.empty_vehicle_weight + td 
        rt.cost = tn_km    


    def create_initial_routes(self):
        s = Solution()
        for i in range(len(self.customers)):
            n = self.customers[i]
            rt = Route(self.depot, self.capacity, self.empty_vehicle_weight)
            n.route = rt
            n.position_in_route = 1
            rt.sequenceOfNodes.insert(1, n)
            s.routes.append(rt)
        return s
    

    def calculate_savings(self):
        savings = []
        for i in range(len(self.customers)):
            n1 = self.customers[i]
            for j in range(i + 1, len(self.customers)): #anw trigwnikos pinakas
                n2 = self.customers[j]

                score = (self.empty_vehicle_weight + n2.demand)*self.distanceMatrix[self.depot.ID][n2.ID]  # Maybe this is (self.empty_vehicle_weight + n1.demand)*self.distanceMatrix[self.depot.ID][n1.ID]
                score -= (self.empty_vehicle_weight + n1.demand + n2.demand) * self.distanceMatrix[n1.ID][n2.ID]
                
                sav = Saving(n1, n2, score)
                savings.append(sav)
        
        return savings
    
    def Clarke_n_Wright(self):
        self.sol = self.create_initial_routes()
        savings: list = self.calculate_savings()
        savings.sort(key=lambda s: s.score, reverse=True)
        
        for i in range(len(savings)): 
            
            sav = savings[i]
            n1, n2 = sav.n1, sav.n2
            rt1, rt2 = n1.route, n2.route

            
            if n1.route == n2.route: #belong to same route
                continue
            if self.not_first_or_last(rt1, n1) or self.not_first_or_last(rt2, n2): #not in the corner
                continue
            if self.onlyDemand(rt1) + self.onlyDemand(rt2) > self.capacity: #capacity overloaded
                continue
            
            self.merge_routes(n1, n2) #mporei na ginei merge 

        self.sol.cost = self.CalculateTotalCost(self.sol)

    def onlyDemand(self,rt):
        td = sum(n.demand for n in rt.sequenceOfNodes) #total demand of rt route
        return td

    def not_first_or_last(self, rt, n):
        if n.position_in_route != 1 and n.position_in_route != len(rt.sequenceOfNodes) - 2:
            return True
        return False
    
    def merge_routes(self, n1, n2):
        rt1 = n1.route
        rt2 = n2.route

        if n1.position_in_route == 1 and n2.position_in_route == len(rt2.sequenceOfNodes) - 2:
            rt1.sequenceOfNodes[1:1] = rt2.sequenceOfNodes[1:len(rt2.sequenceOfNodes) - 1]

        elif n1.position_in_route == 1 and n2.position_in_route == 1:
             for i in range(1, len(rt2.sequenceOfNodes) - 1, 1):
                n = rt2.sequenceOfNodes[i]
                rt1.sequenceOfNodes.insert(1, n)
           
        elif n1.position_in_route == len(rt1.sequenceOfNodes) - 2 and n2.position_in_route == 1:
            rt1.sequenceOfNodes[len(rt1.sequenceOfNodes) - 1:len(rt1.sequenceOfNodes) - 1] = rt2.sequenceOfNodes[1:len(rt2.sequenceOfNodes) - 1]

        elif n1.position_in_route == len(rt1.sequenceOfNodes) - 2 and n2.position_in_route == len(rt2.sequenceOfNodes) - 2:
            rt1.sequenceOfNodes[len(rt1.sequenceOfNodes) - 1:len(rt1.sequenceOfNodes) - 1] = rt2.sequenceOfNodes[len(rt2.sequenceOfNodes) - 2:0:-1]

        self.sol.routes.remove(rt2)
        self.update_route_customers(rt1)

        
    def update_route_customers(self, rt):
        for i in range(1, len(rt.sequenceOfNodes) - 1):
            n = rt.sequenceOfNodes[i]
            n.route = rt
            n.position_in_route = i
