import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import choice, randint
from FSM import *

class Entity(object):
    def __init__(self, node):
        self.name = None
        self.directions = {UP:Vector2(0, -1),DOWN:Vector2(0, 1), 
                          LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0), STOP:Vector2()}
        self.direction = STOP
        self.setSpeed(150)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.randomDirection
        self.setStartNode(node)
        self.image = None

        # FSM   
        # Added constants in "constants.py" file
        self.states = [SEEK, FLEE, WANDER]
        self.myState = WANDER
        self.timer = 0
        self.FSM = StateMachine(self.myState)
        self.init_path = [[], [], [], []]
        self.path = self.init_path
        self.seek_or_flee = True    # seek=True, flee=False
        self.old_state = 0

        self.FSM_decision()

    def setPosition(self):
        self.position = self.node.position.copy()

    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
         
        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()
          
    def validDirection(self, direction):
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp
        
    def oppositeDirection(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions):
        return directions[randint(0, len(directions)-1)]

    def goalDirection(self, directions):
        distances = []
        if self.seek_or_flee:
            for direction in directions:
                vec = self.node.position + self.directions[direction]*TILEWIDTH -  self.goal
                distances.append(vec.magnitudeSquared())
        else:
            for direction in directions:
                vec = self.goal - self.node.position + self.directions[direction]*TILEWIDTH
                distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

    def setStartNode(self, node):
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def setBetweenNodes(self, direction):
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def reset(self):
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100
        self.visible = True

    def setSpeed(self, speed):
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen):
        if self.visible:
            if self.image is not None:
                adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)

    
    def wanderRandom(self, directions):
        return self.randomDirection(directions)

    def wanderBiased(self, directions):
        previousDirection = self.direction
        if previousDirection in directions:
            nextDirProb = randint(1,100)
            if nextDirProb <= 50:
                return previousDirection
            else:
                directions.remove(previousDirection)
                return choice(directions)
        else:
            return self.wanderRandom(directions)

    
    def FSM_decision(self):
        if self.myState == SEEK:
            self.seek_or_flee = True
            self.directionMethod = self.goalDirection
        elif self.myState == FLEE:
            self.seek_or_flee = False
            self.directionMethod = self.goalDirection
        elif self.myState == WANDER:
            self.directionMethod = self.wanderBiased
        else:
            self.myState = choice(self.states)

    # SEEK <--> WANDER --> FLEE
    #  ^---------------------'
    # SEEKtoWANDER = if target is < 2 nodes away
    # WANDERtoSEEK = if character is in top-left half in 2 < x <= 5 seconds
    # WANDERtoFLEE = after 5 seconds
    # FLEEtoSEEK = if character hits one of the corners
    def advancedFSM(self):
        position = self.position
        position = (int(position.x), int(position.y))
        new_state = self.FSM.updateState(self.path, coordinates=position, timer=int(self.timer))
        # print(new_state)
        if new_state == SEEK: 
            self.speed = 80
            self.directionMethod = self.goalDirectionDij
        elif new_state == FLEE:
            self.speed = 180
            self.seek_or_flee = False
            self.directionMethod = self.goalDirection
        elif new_state == WANDER:
            self.speed = 300
            self.directionMethod = self.wanderBiased
        else:
            new_state = choice(self.states)
        if self.old_state != new_state:
            self.timer = 0
        self.old_state = new_state
        self.path = self.init_path