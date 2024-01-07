from VRP_Model import *
from Solver import*
from SolutionDrawer import *

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []

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
        SolDrawer.draw('MinIns', self.sol, self.allNodes)
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

    def InitializeOperators(self, rm):
        rm.Initialize()
    
    def LocalSearch(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()

        while terminationCondition is False:
            self.InitializeOperators(rm)
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)
           
            self.FindBestRelocationMove(rm)
            if rm.originRoutePosition is not None:
                if rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                else:
                    terminationCondition = True

                self.TestSolution()

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1

            print(localSearchIterator, self.sol.cost)

        self.sol = self.bestSolution


    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[originRouteIndex]
            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                for targetRouteIndex in range (0, len(self.sol.routes)):
                    rt2:Route = self.sol.routes[targetRouteIndex]
                    for targetNodeIndex in range (0, len(rt2.sequenceOfNodes) - 1):
                        
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
                        
                        rt1copy = self.cloneRoute(rt1)
                        rt2copy = self.cloneRoute(rt2)

                        moveCost = None
                      
                        if originRouteIndex == targetRouteIndex:

                            del rt1copy.sequenceOfNodes[originNodeIndex]
                            
                            if (originNodeIndex < targetNodeIndex):
                                rt1copy.sequenceOfNodes.insert(targetNodeIndex, B)
                            else:
                                rt1copy.sequenceOfNodes.insert(targetNodeIndex + 1, B)

                            self.UpdateRouteCostAndLoad(rt1copy)

                            moveCost = rt1copy.cost - rt1.cost
                            
                        else:
                            del rt1copy.sequenceOfNodes[originNodeIndex]
                            rt2copy.sequenceOfNodes.insert(targetNodeIndex + 1, B)
        
                            self.UpdateRouteCostAndLoad(rt1copy)
                            self.UpdateRouteCostAndLoad(rt2copy)


                            moveCost = rt1copy.cost + rt2copy.cost - rt1.cost -rt2.cost
                        
                        if (moveCost < rm.moveCost):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, rm)
                            

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, rm:RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
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

            self.UpdateRouteCostAndLoad(originRt)
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
        self.sol.cost += rm.moveCost

        newCost = self.CalculateTotalCost(self.sol)

        #debuggingOnly
        if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
            print('Cost Issue')
            print(oldCost,newCost,rm.moveCost)

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
        