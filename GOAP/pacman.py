from math import sqrt
from turtle import screensize
import pygame
from pygame.locals import *
from vector import Vector2
from random import choice
from constants import *
from entity import Entity
from algorithms import dijkstra, print_result, dijkstra_or_a_star
from GOAP import GOAP

class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node, nodes)
        self.name = PACMAN
        self.color = YELLOW
        self.goal = Vector2()
        self.speed = 150
        self.directionMethod = self.wanderBiased
        self.collideRadius = 5

        # self.myState = FLEE
        
        self.start_dt = self.timer
        self.cornerReached =False

        self.GOAP = GOAP(depth=3)
        self.GOAPtimer = 0
        self.killedFlag = False 
        self.killedTimer = 0
        self.quadrant = None
        self.enemyQuadrant = None
        self.accelerateTimer = 0


    def getGhostObject(self, ghost):
        self.ghost = ghost
        self.enemy = self.ghost
        
    def update(self, dt):
        self.execGOAP(dt)
        self.goal = self.ghost.position
        self.GOAPtimer += dt
        self.killedTimer += dt
        self.timer += dt
        self.accelerateTimer += dt
        self.position += self.directions[self.direction]*self.speed*dt
         
        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()
        
    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius+self.collideRadius)**2
            if dSquared <= rSquared:
                return pellet
        return None

    # EXERCISE 14
    def updateKillFlag(self):
        if self.killedFlag:
            if int(self.killedTimer) >= 15:
                self.killedFlag = False
        else:
            distanceToEnemy = (abs(self.position.x-self.enemy.position.x), 
                            abs(self.position.y-self.enemy.position.y))
            if distanceToEnemy[0] <= 15 and distanceToEnemy[1] <= 15:
                # Set flag to true
                self.killedFlag = True
                # Restart timer from 0, so that it counts how long
                # it has been since enemy was killed.
                self.killedTimer = 0

    def updateQuadrant(self, relevantPosition):
        if relevantPosition.x <= (SCREENWIDTH/2):
            inLeftHalf = True
        else:
            inLeftHalf = False
        if relevantPosition.y <= (SCREENHEIGHT/2):
            inTopHalf = True
        else:
            inTopHalf = False

        if inTopHalf:
            if inLeftHalf:
                return TOP_LEFT
            else:
                return TOP_RIGHT
        else:
            if inLeftHalf:
                return BOT_LEFT
            else:
                return BOT_RIGHT
        
    def execGOAP(self, dt):
        print("________________________")
        self.updateKillFlag()
        self.quadrant = self.updateQuadrant(self.position)
        self.enemyQuadrant = self.updateQuadrant(self.enemy.position)
        nextAction = self.GOAP.run(self.killedFlag, 
                                   self.quadrant,
                                   self.enemyQuadrant,
                                   dt)
        print(nextAction)
        # exit()
    
    def execFollowTarget(self):
        self.goal = self.enemy.position
        self.directionMethod = self.goalDirectionDij

    def execAccelerate(self):
        if self.accelerateTimer <= 3:
            self.speed = 200
        else:
            self.speed = 150
            self.accelerateTimer = 0

    def execGoTargetQuadrant(self):
        res = ()
        if self.enemyQuadrant == TOP_LEFT:
            res = (16,64)
        elif self.enemyQuadrant == TOP_RIGHT:
            res = (416,64)
        elif self.enemyQuadrant == BOT_LEFT:
            res = (16,464)
        elif self.enemyQuadrant == BOT_RIGHT:
            res = (416,464)
        self.goal = Vector2(res)

    def execGoDifferentQuadrant(self):
        quads = [TOP_LEFT, TOP_RIGHT, BOT_LEFT, BOT_RIGHT]
        quad = choice(quads)
        if quad == self.quadrant:
            quad = self.goDifferentQuadrant()
        res = ()
        if quad == TOP_LEFT:
            res = (16,64)
        elif quad == TOP_RIGHT:
            res = (416,64)
        elif quad == BOT_LEFT:
            res = (16,464)
        elif quad == BOT_RIGHT:
            res = (416,464)
        self.goal = Vector2(res)
        return quad

    def execWander(self):
        self.directionMethod = self.wanderBiased

    def execCorner(self):
        if self.quadrant == TOP_LEFT:
            res = (16,64)
        elif self.quadrant == TOP_RIGHT:
            res = (416,64)
        elif self.quadrant == BOT_LEFT:
            res = (16,464)
        elif self.quadrant == BOT_RIGHT:
            res = (416,464)
        self.goal = Vector2(res)