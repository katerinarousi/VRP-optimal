from VRP_Model import *
from Solver import*

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []

class Saving:
    def __init__(self, n1, n2, sav):
        self.n1 = n1
        self.n2 = n2
        self.score = sav

class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9


class Solver1:
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
        self.LocalSearch(0)
        self.RemoveLastDepot(self.sol)
        self.ReportSolution(self.sol)
        self.ReportToFile(self.sol, "example_solution10.txt")
        return self.sol
                
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

    def InitializeOperators(self, rm):
        rm.Initialize()

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
        
    def LocalSearch(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()

        while terminationCondition is False:

            self.InitializeOperators(rm)
            #SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)
            # Relocations
            if operator == 0:
                
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        terminationCondition = True

            #self.TestSolution()

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1
            print(localSearchIterator, self.sol.cost)

        self.sol = self.bestSolution

    def Hallo(self):
        for i in range(0, len(self.sol.routes)):
                    rt=self.sol.routes[i]
                    rt.sequenceOfNodes.append(self.depot)

    def RemoveLastDepot(self,sol):
        for i in range(len(sol.routes)):
            rt = sol.routes[i]
            rt.sequenceOfNodes.pop()
   

    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[originRouteIndex]
            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                for targetRouteIndex in range (0, len(self.sol.routes)):
                    rt2:Route = self.sol.routes[targetRouteIndex]
                    for targetNodeIndex in range (0, len(rt2.sequenceOfNodes) - 1):
                        if targetNodeIndex==len(rt2.sequenceOfNodes) or originNodeIndex==len(rt1.sequenceOfNodes):
                            continue
                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:
                            if rt2.load + B.demand > rt2.capacity:
                                continue

                        costAdded = self.distanceMatrix[A.ID][C.ID] + self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID]
                        costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[B.ID][C.ID] + self.distanceMatrix[F.ID][G.ID]

                        originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - self.distanceMatrix[B.ID][C.ID]
                        targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - self.distanceMatrix[F.ID][G.ID]

                        moveCost = costAdded - costRemoved

                        if (moveCost < rm.moveCost):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm)

    
    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm:RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    
    def ApplyRelocationMove(self, rm: RelocationMove):

        oldCost = self.CalculateTotalCost(self.sol)

        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if (rm.originNodePosition < rm.targetNodePosition):
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.moveCost
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.cost += rm.costChangeOriginRt
            targetRt.cost += rm.costChangeTargetRt
            originRt.load -= B.demand
            targetRt.load += B.demand

        self.sol.cost += rm.moveCost

        newCost = self.CalculateTotalCost(self.sol)
        #debuggingOnly
        if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
            print('Cost Issue')
