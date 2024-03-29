import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from algorithms import dijkstra, print_result, dijkstra_or_a_star
from random import choice

class Ghost(Entity):
    def __init__(self, node, nodes, pacman=None):
        Entity.__init__(self, node)
        self.name = GHOST
        self.points = 200
        self.goal = Vector2()
        self.directionMethod = self.goalDirection
        self.pacman = pacman
        self.nodes = nodes
        self.speed = 80

    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = self.node.position  + self.directions[direction]*TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]
    
    def update(self, dt):
        self.goal = self.pacman.position
        Entity.update(self, dt)

    #############
    # Executes Dijkstra from Ghost's previous node as start 
    # to pacman's target node as target.
    def getDijkstraPath(self, directions):
        lastPacmanNode = self.pacman.target
        lastPacmanNode = self.nodes.getPixelsFromNode(lastPacmanNode)
        ghostTarget = self.target
        ghostTarget = self.nodes.getPixelsFromNode(ghostTarget)

        # previous_nodes, shortest_path = dijkstra(self.nodes, ghostTarget)
        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, ghostTarget, a_star=True)
        path = []
        node = lastPacmanNode
        while node != ghostTarget:
            path.append(node)
            node = previous_nodes[node]
        path.append(ghostTarget)
        path.reverse()
        # print(path)
        return path

    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath(directions)
        print(path)
        nextGhostNode = path[0]
        if len(path) > 1:
            nextNextGhostNode = path[1]
            if nextGhostNode[0] > nextNextGhostNode[0] and 2 in directions: #left
                return 2
            if nextGhostNode[0] < nextNextGhostNode[0] and -2 in directions: #right
                return -2
            if nextGhostNode[1] > nextNextGhostNode[1] and 1 in directions: #up
                return 1
            if nextGhostNode[1] < nextNextGhostNode[1] and -1 in directions: #down
                return -1
            else: 
                return choice(directions)
        else:
            # IF THEY ARE ABOUT TO COLLIDE
            ghostTarget = self.target
            ghostTarget = self.nodes.getPixelsFromNode(ghostTarget)
            if ghostTarget[0] > nextGhostNode[0] and 2 in directions : #left
                return 2
            if ghostTarget[0] < nextGhostNode[0] and -2 in directions : #right
                return -2
            if ghostTarget[1] > nextGhostNode[1] and 1 in directions : #up
                return 1
            if ghostTarget[1] < nextGhostNode[1] and -1 in directions : #down
                return -1
            else:
                return choice(directions)
        
        # up 1, down -1, left 2, right -2


    # Ghost can get stuck when having to reverse its direction
    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                # if key != self.direction * -1:
                directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions