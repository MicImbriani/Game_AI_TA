import copy

class WorldModel(object):
    def __init__(self, goals, timer, actions):
        self.goals = copy.copy(goals)
        self.highestGoal = None
        self.actions = copy.copy(actions)
        self.timer = timer
        self.unvisitedActions = copy.copy(self.actions)
        
        self.setHighestGoal()
    
    # Finds the goal with highest priority
    def setHighestGoal(self):
        maxValuedGoal = 0
        currentMaxGoal = self.goals[0]
        for goal in self.goals:
            if goal.value > maxValuedGoal:
                maxValuedGoal = goal.value
                currentMaxGoal = goal
        self.highestGoal = currentMaxGoal
        # print("HIGHEST:       ", self.highestGoal.name)
    
    # Returns square of goal with max priority
    def calculateDiscontentment(self):
        return self.highestGoal.getDiscontentment()
    
    # Returns the next unvisited action. 
    # Uses counter to keep track of visited actions.
    def nextAction(self):
        if len(self.unvisitedActions) > 0:
            return self.unvisitedActions.pop(0)
        else:
            return None
    def applyAction(self, action):
        action.getGoalChange(self.highestGoal)