import sys
import copy
from vector import Vector2
from threading import Timer
from constants import *

class Goal(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    # added in second part of exercise
    def getDiscontentment(self):
        return (self.value * self.value)
    def updateValue(self, newValue):
        self.value = newValue


class Action(object):
    def __init__(self, name):
        self.name = name
        self.value = 0
    
    def getGoalChange(self, goal):
        return

######
class FollowPathToTarget(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 5
    def getGoalChange(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value +=100

class GoInSameQuadrant(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 4
    def getGoalChange(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value +=100

class Accelerate(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 2
    def getGoalChange(self, goal):
        if goal.name == KILL_GHOST:
            goal.value -= self.value
        else:
            goal.value +=100

####
class VisitAnotherQuadrant(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 4
    def getGoalChange(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value +=100

class Wander(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 10
    def getGoalChange(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value +=100

class GoClosestCorner(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 2
    def getGoalChange(self, goal):
        if goal.name == EAT_SUPERPELLETS:
            goal.value -= self.value
        else:
            goal.value +=100

class Dummy(Action):
    def __init__(self, name):
        Action.__init__(self, name)
        self.value = 1
    def getGoalChange(self, goal):
        goal.value -= self.value
        