import copy
import pickle
from deap import base
from deap import creator 
from deap import tools

import random
import time
import numpy as np

from run import GameController




"""
PREMISES FOR EXERCISE:
1) ONLY ONE GHOST.
2) EVEN WHEN IN "EATABLE" MODE, STILL CHASES PACMAN
3) PACMAN ALWAYS FLEES.
4) BECAUSE OF 2) AND 3), THE PATH TAKEN WILL ALWAYS BE THE SAME
5) GOOD FOR REPLICABILITY PURPOSES. ALL INDIVIDUALS ASSESSED FAIRLY
6) BAD BECAUSE IT WILL BE ADAPT TO THIS SPECIFIC PATH ONLY
"""

# 241 pellets in total. If 1 fruit spawns every 30 pellets,
# the max # of fruits possible is 8. +1 so it there will always be one more to pop
IND_SIZE = 9

# Initialize game, so that we can retrieve list of nodes.
game = GameController()
game.startGame()
possible_positions = game.nodes.getListOfNodesVector()
print("POSSIBLE NODES:")
print(possible_positions)
print("___________________________________")

# Create the fitness function. 
# Weights is 1.0 --> Maximization problem
# Comma after the 1.0 because we COULD train to fit to multiple objectives.
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# Create the blue-print for how an individual will look like.
# It will be a LIST containing the positions of the spawned fruits.
# We will set the fitness function we just created as the fitness criterion
# against which each individual will be evaluated.
creator.create("Individual", list, fitness=creator.FitnessMax)

# In DEAP, toolbox is the core functionality for using Ev. algs.
toolbox = base.Toolbox()
# Construct an individual by repeatedly randomly picking a position in which
# to place a fruit from the possible positions.
toolbox.register("attribute", random.choice, possible_positions)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)

# Function for running one iteration of the game.
# Takes the individual's list of positions in which to place the 
# fruits, and passes it to the game. Only runs for 1 life.
# Returns score and fruits eaten.
def run_game(indiv):
    game = GameController()
    game.startGame()
    game.getListOfFruitPos(indiv)
    while game.lives > 4:
        game.update()
    score = game.score
    fruits = len(game.fruitEaten)
    # distances_pac = game.distances_pac
    # distances_ghost = game.distances_ghost
    del game
    return score, fruits

# Evaluation function.
def evaluate(indiv, generation):
    print("GEN:   ", generation)
    print("Individual:   ", indiv)
    score, fruits = run_game(copy.copy(indiv))
    print("Score:   ", score)
    print("Fruits eaten:   ", fruits)
    # MODIFY HERE TO CHANGE HOW FITNESS IS COMPUTED.
    # +1 because roulette selection doesn't work with fitness <= 0.
    fitness = score * fruits + 1
    print("FITNESS:   ", fitness)
    print("END")
    print("____________")
    print()
    print()
    return int(fitness),

# Some functions for the mutation of individuals.
toolbox.register("evaluate", evaluate)
# Select *k* individuals from the 
# input *individuals* using *k* spins of a roulette.
toolbox.register("select", tools.selRoulette)
# Two-point crossover.
toolbox.register("crossover", tools.cxTwoPoint)
# Population is generated by repeatedly creating new individuals.
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Mutation function
# For each fruit, randomly (i.e. using indpb) decide to change the
# position to the node before or after.
def mutate(indiv, indpb):
    for fruit_position, index in zip(indiv, range(len(indiv))):
        if random.random() < indpb:
            pos_id = possible_positions.index(fruit_position)
            if index < len(indiv):
                new_pos = random.choice([possible_positions[pos_id-1], 
                                        possible_positions[pos_id+1]])
            else:
                new_pos = random.choice([possible_positions[pos_id-2], 
                                        possible_positions[pos_id-1]])
            indiv[index] = new_pos
        else:
            continue
    return indiv

toolbox.register("mutate", mutate, indpb=0.05)

# Some functions for computing useful statistics about the results.
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

# For registering results.
logbook = tools.Logbook()

# Generate population.
pop = toolbox.population(n=100)

# Compute first round of fitnesses for first generation.
fitness = [toolbox.evaluate(indiv, 1) for indiv in pop]
print(fitness)

# Assign the fitnesses to each individual.
for ind, fit in zip(pop, fitness):
    ind.fitness.values = fit

# Generation to train for
NGEN = 500
# Crossover Probability
CXPB = 0.2

# The evolutionary iteration step starts here.
for gen in range(NGEN):
    print("--GEN: {}-----------------------------------------------".format(gen))

    offspring = toolbox.select(pop, len(pop))
    print("OFF", offspring)
    offspring = list(map(toolbox.clone, offspring))
    print("OFF", offspring)
    # ^ because toolbox.select returns a reference to the individuals
    
    # Crossover.
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.crossover(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
    
    # Mutate.
    for mutant in offspring:
        toolbox.mutate(mutant)
        del mutant.fitness.values
    

    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    print(invalid_ind)
    fitnesses = [toolbox.evaluate(indiv, gen) for indiv in invalid_ind]
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    
    # Record results from current generation.
    pop[:] = offspring
    record = stats.compile(pop)
    logbook.record(gen=gen, **record)




logbook.header = "gen", "avg", "evals", "std", "min", "max"

import matplotlib.pyplot as plt
gen = logbook.select("gen")
avgs = logbook.select("avg")
stds = logbook.select("std")
min = logbook.select("min")
max = logbook.select("max")



plt.rc('axes', labelsize=14)
plt.rc('xtick', labelsize=14)
plt.rc('ytick', labelsize=14) 
plt.rc('legend', fontsize=14)

fig, ax1 = plt.subplots()
#line1 = ax1.plot(gen, avgs)
line1 = ax1.errorbar(gen, avgs, yerr=stds, errorevery=2)
ax1.set_xlabel("Generation")
ax1.set_ylabel("Mean Fitness")


fig, ax1 = plt.subplots()
#line1 = ax1.plot(gen, avgs)
line1 = ax1.errorbar(gen, min, yerr=stds, errorevery=2)
ax1.set_xlabel("Generation")
ax1.set_ylabel("Worst Individuals")


fig, ax1 = plt.subplots()
#line1 = ax1.plot(gen, avgs)
line1 = ax1.errorbar(gen, max, yerr=stds, errorevery=2)
ax1.set_xlabel("Generation")
ax1.set_ylabel("Best Individuals")


def averageOfList(num):
    sumOfNumbers = 0
    for t in num:
        sumOfNumbers = sumOfNumbers + t

    avg = sumOfNumbers / len(num)
    return avg

print("Average score: ", averageOfList(avgs))
print("Highest average score: ", np.max(avgs))
print("Lowest average score: ", np.min(avgs))

print("Best high scoring individual: ", np.max(max))
print("Worst high scoring individual: ", np.min(max))

print()
print("Best low scoring individual: ", np.max(min))
print("Worst low scoring individual: ",np.min(min))


# Save the Best individual.
def savePolicy():
    fw = open('best_individual', 'wb')
    pickle.dump(bestInd, fw)
    fw.close()

# Loads a Q-table.
def loadPolicy(file):
    fr = open(file, 'rb')
    bestInd = pickle.load(fr)
    fr.close()

bestInd = tools.selBest(pop, 1)[0]
savePolicy()

fitness = run_game(bestInd)