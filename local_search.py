from VRP_Model import *
from SolutionDrawer import *

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


class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.cost = 10 ** 9

class CustomerInsertionAllPositions(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.insertionPosition = None
        self.cost = 10 ** 9

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





class local_search:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.empty_vehicle_weight = m.empty_vehicle_weight
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.Clarke_n_Wright()
        self.RemoveLastDepot(self.sol)
        self.ReportSolution(self.sol)
        #self.ReportToFile(self.sol, "example_solution.txt")
        self.LocalSearch(2)
        self.ReportSolution(self.sol)
        self.ReportToFile(self.sol, "example_solution.txt")
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False


    def LocalSearch(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        while terminationCondition is False:

            self.InitializeOperators(rm, sm, top)
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

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
            print(localSearchIterator, self.sol.cost)

        self.sol = self.bestSolution

    def cloneRoute(self, rt:Route):
        cloned = Route(self.depot, self.capacity, self.empty_vehicle_weight)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.empty_vehicle_weight = rt.empty_vehicle_weight
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

                        costAdded = self.distanceMatrix[A.ID][C.ID] + self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID]
                        costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[B.ID][C.ID] + self.distanceMatrix[F.ID][G.ID]

                        originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - self.distanceMatrix[B.ID][C.ID]
                        targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - self.distanceMatrix[F.ID][G.ID]

                        moveCost = costAdded - costRemoved

                        if (moveCost < rm.moveCost):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm)

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

                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                # case of consecutive nodes swap
                                costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + \
                                              self.distanceMatrix[b2.ID][c2.ID]
                                costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + \
                                            self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved
                            else:

                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        else:
                            if rt1.load - b1.demand + b2.demand > self.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                            costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                            costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                            costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2

                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                        if moveCost < sm.moveCost:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

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


    def ApplySwapMove(self, sm):
       oldCost = self.CalculateTotalCost(self.sol)
       rt1 = self.sol.routes[sm.positionOfFirstRoute]
       rt2 = self.sol.routes[sm.positionOfSecondRoute]
       b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
       b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
       rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
       rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

       if (rt1 == rt2):
           rt1.cost += sm.moveCost
       else:
           rt1.cost += sm.costChangeFirstRt
           rt2.cost += sm.costChangeSecondRt
           rt1.load = rt1.load - b1.demand + b2.demand
           rt2.load = rt2.load + b1.demand - b2.demand

       self.sol.cost += sm.moveCost

       newCost = self.CalculateTotalCost(self.sol)
       # debuggingOnly
       if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
           print('Cost Issue')

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print(rt.cost)
        #SolDrawer.draw('MinIns', self.sol, self.allNodes)
        print (self.sol.cost)

    def GetLastOpenRoute(self):
        if len(self.sol.routes) == 0:
            return None
        else:
            return self.sol.routes[-1]

    def IdentifyBestInsertion(self, bestInsertion, rt):
        for i in range(0, len(self.customers)):
            candidateCust:Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                    trialCost = self.distanceMatrix[lastNodePresentInTheRoute.ID][candidateCust.ID]
                    if trialCost < bestInsertion.cost:
                        bestInsertion.customer = candidateCust
                        bestInsertion.route = rt
                        bestInsertion.cost = trialCost

    def ApplyCustomerInsertion(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        #before the second depot occurrence
        insIndex = len(rt.sequenceOfNodes) - 1
        rt.sequenceOfNodes.insert(insIndex, insCustomer)

        beforeInserted = rt.sequenceOfNodes[-3]

        costAdded = self.distanceMatrix[beforeInserted.ID][insCustomer.ID] *  + self.distanceMatrix[insCustomer.ID][self.depot.ID] 
        costRemoved = self.distanceMatrix[beforeInserted.ID][self.depot.ID]

        rt.cost += costAdded - costRemoved
        self.sol.cost += costAdded - costRemoved

        rt.load += insCustomer.demand

        insCustomer.isRouted = True

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm:RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

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

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            costAdded = self.distanceMatrix[A.ID][K.ID] * (self.empty_vehicle_weight + A.demand + K.demand) + self.distanceMatrix[B.ID][L.ID] * (self.empty_vehicle_weight + B.demand + L.demand)
                            costRemoved = self.distanceMatrix[A.ID][B.ID] * (self.empty_vehicle_weight + A.demand + B.demand) + self.distanceMatrix[K.ID][L.ID] * (self.empty_vehicle_weight + K.demand + L.demand)
                            moveCost = costAdded - costRemoved
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and  nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue
                            costAdded = self.distanceMatrix[A.ID][L.ID] * (self.empty_vehicle_weight + A.demand + L.demand)+ self.distanceMatrix[B.ID][K.ID] * (self.empty_vehicle_weight + B.demand + K.demand)
                            costRemoved = self.distanceMatrix[A.ID][B.ID] * (self.empty_vehicle_weight + A.demand + B.demand) + self.distanceMatrix[K.ID][L.ID] * (self.empty_vehicle_weight + K.demand + L.demand)
                            moveCost = costAdded - costRemoved
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

            rt1.cost += top.moveCost

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

        self.sol.cost += top.moveCost

    def TestSolution(self):
        totalSolCost = 0
        for r in range (0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            for n in range (0 , len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.distanceMatrix[A.ID][B.ID] * (self.empty_vehicle_weight + A.demand + B.demand) # Study this one better 
                rtLoad += A.demand
            if abs(rtCost - rt.cost) > 0.0001:
                print ('Route Cost problem')
            if rtLoad != rt.load:
                print ('Route Load problem')

            totalSolCost += rt.cost

        if abs(totalSolCost - self.sol.cost) > 0.0001:
            print('Solution Cost problem')

    def IdentifyMinimumCostInsertion(self, best_insertion):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                for rt in self.sol.routes:
                    if rt.load + candidateCust.demand <= rt.capacity:
                        for j in range(0, len(rt.sequenceOfNodes) - 1):
                            A = rt.sequenceOfNodes[j]
                            B = rt.sequenceOfNodes[j + 1]
                            costAdded = self.distanceMatrix[A.ID][candidateCust.ID] * (self.empty_vehicle_weight + candidateCust.demand + A.demand) + self.distanceMatrix[candidateCust.ID][
                                B.ID] * (self.empty_vehicle_weight + candidateCust.demand + B.demand)
                            costRemoved = self.distanceMatrix[A.ID][B.ID] * (self.empty_vehicle_weight + A.demand + B.demand)
                            trialCost = costAdded - costRemoved
                            if trialCost < best_insertion.cost:
                                best_insertion.customer = candidateCust
                                best_insertion.route = rt
                                best_insertion.insertionPosition = j
                                best_insertion.cost = trialCost
                    else:
                        continue

    def ApplyCustomerInsertionAllPositions(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        # before the second depot occurrence
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insCustomer)
        rt.cost += insertion.cost
        self.sol.cost += insertion.cost
        rt.load += insCustomer.demand
        insCustomer.isRouted = True

    
    # Clarke_n_Wright implementation from first solution
    def RemoveLastDepot(self,sol):
        for i in range(len(sol.routes)):
            rt = sol.routes[i]
            rt.sequenceOfNodes.pop()
                


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

                score = (self.empty_vehicle_weight + n1.demand) * self.distanceMatrix[self.depot.ID][n1.ID]  # Maybe this is (self.empty_vehicle_weight + n1.demand)*self.distanceMatrix[self.depot.ID][n1.ID]
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

