import numpy as np
from itertools import zip_longest
from bird import Bird
from flappy import Flappy
from config import *
from utils import generate_random_force

def grouper(population, group_size, fillvalue=Bird()):
    group = [iter(population)] * group_size
    return zip_longest(*group, fillvalue=fillvalue)


def tournament(population, group_size=10):
    # Tournament
    team_size = int(group_size / 2)
    for group in grouper(population, group_size=group_size):
        team_1, team_2 = group[:team_size], group[team_size:]

        winner_1 = max(team_1, key=lambda bird: bird.fitness)
        winner_2 = max(team_2, key=lambda bird: bird.fitness)

        yield (winner_1, winner_2)


def accept_reject(population, runs):
    max_fitness = max(population, key=lambda bird: bird.fitness).fitness
    
    def sample():
        while True:
            index = np.random.randint(len(population))
            r = np.random.uniform(max_fitness)

            parent = population[index]
            if r < parent.fitness:
                return parent

    for _ in range(runs):
        yield (sample(), sample())
    

def crossover(parent_1, parent_2):
    HALF = int(MAX_LIFE / 2)
    
    children = [Bird(), Bird()]
    children[0].genes = parent_1.genes[:HALF] + parent_2.genes[HALF:]
    children[1].genes = parent_2.genes[:HALF] + parent_1.genes[:HALF]

    return children


def mutate(bird, rate):
    mutation = np.random.uniform(size=MAX_LIFE) < rate
    for i, mutate in enumerate(mutation):
        if mutate:
            bird.genes[i] = generate_random_force()


game = Flappy()

ELITISM = True
MUTATION_RATE = 0.01

@game.register_ai
def super_ai(birds):
    new_population = []
    
    if ELITISM:
        elite_bird = max(birds, key=lambda bird: bird.fitness)
        new_population.append(elite_bird)

    for parent_1, parent_2 in accept_reject(birds, runs=int(MAX_POPULATION / 2)):
        # Crossover
        for child in crossover(parent_1, parent_2):
            # Mutation
            mutate(child, rate=MUTATION_RATE)

            # Add children to the new population
            new_population.append(child)
        
    # Re-fill population
    d_pop = MAX_POPULATION - len(new_population)
    new_population += [Bird() for _ in range(d_pop)]

    return new_population

game.start()