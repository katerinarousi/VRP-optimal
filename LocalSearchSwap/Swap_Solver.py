from VRP_Model import *
from SolutionDrawer import *

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9

class Solver2:
    def __init__(self, m, initial_solution):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.empty_vehicle_weight = m.empty_vehicle_weight
        self.sol = initial_solution
        self.bestSolution = None

    def solve(self):
        self.Hallo()
        self.LocalSearch()
        self.RemoveLastDepot(self.sol)
        self.ReportSolution(self.sol)
        self.ReportToFile(self.sol, "example_solution20.txt")
        return self.sol

    def Hallo(self):
        for i in range(0, len(self.sol.routes)):
                    rt=self.sol.routes[i]
                    rt.sequenceOfNodes.append(self.depot)

    def RemoveLastDepot(self,sol):
        for i in range(len(sol.routes)):
            rt = sol.routes[i]
            rt.sequenceOfNodes.pop()
   
    def ReportSolution(self, sol):
        for i in range(len(sol.routes)):
            rt = sol.routes[i]
            for j in range (len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print(rt.cost, rt.load)
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
  
    def LocalSearch(self):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        sm = SwapMove()

        while terminationCondition is False:

            self.InitializeOperators(sm)
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)
            self.flag = False
            self.counter = 0
            self.FindBestSwapMove(sm)
            if sm.positionOfFirstRoute is not None:
                if sm.moveCost < 0 and self.flag == False:
                    self.ApplySwapMove(sm)
                else:
                    terminationCondition = True
            
            self.TestSolution()

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1
            self.CalculateTotalCost(self.sol)
            print(localSearchIterator, self.sol.cost)

        self.sol = self.bestSolution

    
    def FindBestSwapMove(self, sm):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[firstRouteIndex]
            for secondRouteIndex in range (firstRouteIndex, len(self.sol.routes)):
                rt2:Route = self.sol.routes[secondRouteIndex]
                for firstNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range (startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                        #a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        #c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        #a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        #c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]
                        
                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        rt1copy = self.cloneRoute(rt1)
                        rt2copy = self.cloneRoute(rt2)
                        
                        if rt1 == rt2:
                            rt1copy.sequenceOfNodes[firstNodeIndex] = b2
                            rt1copy.sequenceOfNodes[secondNodeIndex] = b1
                            self.UpdateRouteCostAndLoad(rt1copy)
                            moveCost = rt1copy.cost - rt1.cost
                        
                        else:
                            if rt1.load - b1.demand + b2.demand > self.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            rt1copy.sequenceOfNodes[firstNodeIndex] = b2
                            rt2copy.sequenceOfNodes[secondNodeIndex] = b1

                            self.UpdateRouteCostAndLoad(rt1copy)
                            self.UpdateRouteCostAndLoad(rt2copy)
                            moveCost = rt1copy.cost - rt1.cost + rt2copy.cost - rt2.cost
                            costChangeFirstRoute = rt1copy.cost - rt1.cost
                            costChangeSecondRoute = rt2copy.cost - rt2.cost
                       
                        
                        if moveCost < sm.moveCost:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

   
    def ApplySwapMove(self, sm):
       oldCost = self.CalculateTotalCost(self.sol)
       rt1 = self.sol.routes[sm.positionOfFirstRoute]
       rt2 = self.sol.routes[sm.positionOfSecondRoute]
       b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
       b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
       rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
       rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

       self.UpdateRouteCostAndLoad(rt1)
       self.UpdateRouteCostAndLoad(rt2)

       newCost = self.CalculateTotalCost(self.sol)
       # debuggingOnly
       if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
           print('Cost Issue', newCost- oldCost, sm.moveCost)
  

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

    
    def InitializeOperators(self, sm):
        sm.Initialize()
           
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
            tl -= B.demand 
        
        rt.load = td #+self.empty_vehicle_capacity an thelw se klimaka mexri 14
        rt.cost = tn_km    

    def TestSolution(self):
        totalSolCost = 0
        for r in range (0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            td = sum(n.demand for n in rt.sequenceOfNodes) #total demand of rt route
            rtLoad = self.empty_vehicle_weight + td 
            rtCost = 0
            for n in range (0 , len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.distanceMatrix[A.ID][B.ID] * rtLoad
                rtLoad -= B.demand
            rtLoad = td
            if abs(rtCost - rt.cost) > 0.0001:
                print ('Route Cost problem')
            if rtLoad != rt.load:
                print ('Route Load problem')

            totalSolCost += rt.cost

        if abs(totalSolCost - self.sol.cost) > 0.0001:
            print('Solution Cost problem')

    def cloneRoute(self, rt:Route):
        cloned = Route(self.depot, self.capacity, self.empty_vehicle_weight)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
        cloned.cost = self.sol.cost
        return cloned

    