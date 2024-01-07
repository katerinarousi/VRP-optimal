from VRP_Model import *
from Solver import *
#from SolutionDrawer import *

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


class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9


class SolverVND:
    def __init__(self, m, initial_solution):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.empty_vehicle_weight = m.empty_vehicle_weight
        self.sol = initial_solution
        self.bestSolution = None
        self.searchTrajectory = []

    def solve(self):
        self.AddDepotAtTheEndOfEachRoute()
        self.VND()
        self.RemoveLastDepot(self.sol)
        self.ReportSolution(self.sol)
        self.ReportToFile(self.sol, "example_solution2.txt")
        return self.sol

    def AddDepotAtTheEndOfEachRoute(self):
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

    def LocalSearch(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        while terminationCondition is False:

            self.InitializeOperators(rm, sm, top)
            #SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        terminationCondition = True
            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    if sm.moveCost < 0:
                        self.ApplySwapMove(sm)
                    else:
                        terminationCondition = True
            elif operator == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    if top.moveCost < 0:
                        self.ApplyTwoOptMove(top)
                    else:
                        terminationCondition = True

            self.TestSolution()

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1

        self.sol = self.bestSolution

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0
        draw = True

        while k <= kmax:
            self.InitializeOperators(rm, sm, top)
            if k == 2:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    #if draw:
                        #SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 0
                else:
                    k += 1
            elif k == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    #if draw:
                        #SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 0
                else:
                    k += 1
            elif k == 0:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None and top.moveCost < 0:
                    self.ApplyTwoOptMove(top)
                    #if draw:
                        #SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 0
                else:
                    k += 1

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

        #SolDrawer.draw('final_vnd', self.bestSolution, self.allNodes)
        #SolDrawer.drawTrajectory(self.searchTrajectory)



    def ApplyMove(self, moveStructure):
        if isinstance(moveStructure, RelocationMove):
            self.ApplyRelocationMove(moveStructure)
        elif isinstance(moveStructure, SwapMove):
            self.ApplySwapMove(moveStructure)
        elif isinstance(moveStructure, TwoOptMove):
            self.ApplyTwoOptMove(moveStructure)

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

            self.UpdateRouteCostAndLoad(originRt)
            self.UpdateRouteCostAndLoad(targetRt)
        self.sol.cost += rm.moveCost

        newCost = self.CalculateTotalCost(self.sol)

        #debuggingOnly
        if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
            print('Cost Issue')
            print(oldCost, newCost, rm.moveCost)


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


    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost


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

    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()

    def FindBestTwoOptMove(self, top):
        for rtInd1 in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.sol.routes)):
                rt2:Route = self.sol.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2
                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):
                        moveCost = 10 ** 9

                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]
                        

                        rt1copy = self.cloneRoute(rt1)
                        rt2copy = self.cloneRoute(rt2)

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue

                            reversedSegment = reversed(rt1copy.sequenceOfNodes[nodeInd1 + 1: nodeInd2 + 1])
                            rt1copy.sequenceOfNodes[nodeInd1 + 1 : nodeInd2 + 1] = reversedSegment

                            self.UpdateRouteCostAndLoad(rt1copy)
                            
                            moveCost = rt1copy.cost - rt1.cost
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and  nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue

                            relocatedSegmentOfRt1 = rt1copy.sequenceOfNodes[nodeInd1 + 1 :]
                            relocatedSegmentOfRt2 = rt2copy.sequenceOfNodes[nodeInd2 + 1 :]

                            del rt1copy.sequenceOfNodes[nodeInd1 + 1 :]
                            del rt2copy.sequenceOfNodes[nodeInd2 + 1 :]

                            rt1copy.sequenceOfNodes.extend(relocatedSegmentOfRt2)
                            rt2copy.sequenceOfNodes.extend(relocatedSegmentOfRt1)

                            self.UpdateRouteCostAndLoad(rt1copy)
                            self.UpdateRouteCostAndLoad(rt2copy)
                            
                            moveCost = rt1copy.cost - rt1.cost + rt2copy.cost - rt2.cost

                        if moveCost < top.moveCost:
                            self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top)

    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):

        rt1FirstSegmentLoad = 0
        for i in range(0, nodeInd1 + 1):
            n = rt1.sequenceOfNodes[i]
            rt1FirstSegmentLoad += n.demand
        rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

        rt2FirstSegmentLoad = 0
        for i in range(0, nodeInd2 + 1):
            n = rt2.sequenceOfNodes[i]
            rt2FirstSegmentLoad += n.demand
        rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

        if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity):
            return True
        if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity):
            return True

        return False

    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost

    def ApplyTwoOptMove(self, top):
        oldCost = self.CalculateTotalCost(self.sol)
        rt1:Route = self.sol.routes[top.positionOfFirstRoute]
        rt2:Route = self.sol.routes[top.positionOfSecondRoute]

        if rt1 == rt2:
            # reverses the nodes in the segment [positionOfFirstNode + 1,  top.positionOfSecondNode]
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            #lst = list(reversedSegment)
            #lst2 = list(reversedSegment)
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1 : top.positionOfSecondNode + 1] = reversedSegment

            #reversedSegmentList = list(reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1]))
            #rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegmentList

            self.UpdateRouteCostAndLoad(rt1)

        else:
            #slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :]

            #slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1 :]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1 :]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            self.UpdateRouteCostAndLoad(rt1)
            self.UpdateRouteCostAndLoad(rt2)

        newCost = self.CalculateTotalCost(self.sol)
        # debuggingOnly
        if abs((newCost - oldCost) - top.moveCost) > 0.0001:
           print('Cost Issue', newCost- oldCost, top.moveCost)
        self.CalculateTotalCost(self.sol)

    