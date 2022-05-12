import sys
import copy
from vector import Vector2
from threading import Timer
from constants import *
from goalAndActions import *
from goalAndActions import *
from world import *

class GOAP(object):
    def __init__(self, depth):
        self.depth = depth
        self.timer = 0
        self.worldState = None

        # GOALS
        self.killGhost = Goal(KILL_GHOST, 1)
        # self.wander = Goal(WANDER, 2)
        self.eatSuperpellets = Goal(EAT_SUPERPELLETS, 100)
        self.goals = [self.killGhost, self.eatSuperpellets]

        # ACTIONS FOR GOAL: KILL_GHOST
        self.followPathToTarget = FollowPathToTarget(FOLLOW_PATH_TO_TARGET)
        self.goInSameQuadrant = GoInSameQuadrant(GO_IN_SAME_QUADRANT)
        self.accelerate = Accelerate(ACCELERATE)
        
        # ACTIONS FOR GOAL: EAT_SUPERPELLETS
        self.visitAnotherQuadrant = VisitAnotherQuadrant(VISIT_ANOTHER_QUADRANT)
        self.wander = Wander(WANDER)
        self.goClosestCorner= GoClosestCorner(GO_CLOSEST_CORNER)
        self.dummy = Dummy("DUMMY")
        
        self.actionsKILL = [self.followPathToTarget, self.goInSameQuadrant, self.accelerate]
        self.actionsEAT = [self.visitAnotherQuadrant, self.wander, self.goClosestCorner]
        self.actions = self.actionsKILL + self.actionsEAT + [self.dummy]
        # self.actions = self.actionsEAT

    def updateWorldState(self):
        self.worldState = WorldModel(self.goals, 
                                     self.timer, 
                                     self.actions)

    def planAction(self, worldModel, maxDepth):
        # Create storage for world models at each depth, and
        # actions that correspond to them
        models = [None] * int(len(self.actions)+10) #WorldModel(maxDepth+1)
        actions = [None] * int(len(self.actions)) #Action(maxDepth)
        
        # Set up the initial data
        models[0] = worldModel
        currentDepth = 0

        # Keep track of the best action
        bestAction = None
        bestValue = sys.maxsize

        # Iterate until we have completed all actions at depth 0
        while currentDepth >= 0:
            # Calculate the discontentment value
            currentValue = models[currentDepth].calculateDiscontentment()
            # Check if we're at maximum depth
            # print(currentDepth)
            if currentDepth >= maxDepth:
                # If current value is best, store it
                if currentValue < bestValue:
                    bestValue = currentValue
                    bestAction = actions[0]
                    # print("CUR VAL:", currentValue)
                    # print(bestAction)
                    # We're done at this depth, so drop back
                    currentDepth -= 1
                    #Jump to next iteration
                    continue

            # Otherwise, we need to try the next action
            nextAction = models[currentDepth].nextAction()
            if nextAction:
                # We have an action to apply, copy the current model
                models[currentDepth+1] = copy.deepcopy(models[currentDepth])
                # and apply the action to the copy
                actions[currentDepth] = nextAction
                models[currentDepth+1].applyAction(nextAction)
                models[currentDepth+1].setHighestGoal()
                # print("CHOSEN ACTION", nextAction.name)
                # print("_____")

                # and process it on the next iteration
                currentDepth += 1

            # Otherwise we have no action to try, so we’re 
            # done at this level
            else:
                # Drop back to the next highest level
                currentDepth -= 1

        # We've finished iterating, so return the result
        return bestAction

    # Method for checking if goal values have to change.
    # In this implementation, it's based on killFlag.
    def updateGoalsValues(self, killFlag):
        if killFlag:
            self.killGhost.value = 1
            self.eatSuperpellets.value = 1000
        else:
            self.killGhost.value = 1000
            self.eatSuperpellets.value = 1

    def updateActionsValues(self, myQuadrant, enemyQuadrant):
        # KILL ENEMY ACTIONS
        # If I am in same quadrant
        if myQuadrant == enemyQuadrant: 
            self.follow_acc_quad()
        # If I am in diagonally opposite quadrant of enemy
        elif myQuadrant == enemyQuadrant * -1:
            self.quad_acc_follow()
        else:
            self.acc_quad_follow()

        # EAT PELLETS ACTIONS
        # Rotate between actions:
        # 1) go to closest corner
        # 2) wander
        # 3) go to different quadrant
        # 4) repeat
        print(self.timer)
        if self.timer >= 0. and self.timer <= 2.:
            self.corner_wander_changequad()
        elif self.timer > 2. and self.timer <= 6.:
            self.wander_changequad_corner()
        elif self.timer > 6. and self.timer <= 11.:
            self.changequad_wander_corner()
        else:
            self.timer = 0.

    def run(self, killFlag, quadrant, enemyQuadrant, dt):
        self.timer += dt
        self.updateWorldState()
        self.updateGoalsValues(killFlag)
        self.updateActionsValues(quadrant, enemyQuadrant)
        currentWorldModel = WorldModel(self.goals,
                                       self.timer, 
                                       self.actions)
        nextAction = self.planAction(self.worldState, self.depth)
        return nextAction

    def quad_acc_follow(self):
        self.goInSameQuadrant.value = 100
        self.accelerate.value = 5
        self.followPathToTarget.value = 1
    
    def acc_quad_follow(self):
        self.accelerate.value = 100
        self.goInSameQuadrant.value = 5
        self.followPathToTarget.value = 2

    def follow_acc_quad(self):
        self.followPathToTarget.value = 100
        self.accelerate.value = 5
        self.goInSameQuadrant.value = 2
    ##############################################
    def changequad_wander_corner(self):
        self.visitAnotherQuadrant.value = 100
        self.wander.value = 5
        self.goClosestCorner.value = 1
    
    def wander_changequad_corner(self):
        self.wander.value = 100
        self.visitAnotherQuadrant.value = 5
        self.goClosestCorner.value = 1
    
    def corner_wander_changequad(self):
        self.goClosestCorner.value = 100
        self.wander.value = 5
        self.visitAnotherQuadrant.value = 1