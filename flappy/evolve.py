import random
import numpy as np
from itertools import zip_longest
from bird import Bird
from flappy import Flappy
from config import *
from utils import generate_random_force

stats = {
    'mutations': 0
}

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
    for bird in population:
        try:
            bird.fitness /= max_fitness
        except ZeroDivisionError:
            bird.fitness = random.uniform()

    def sample():
        while True:
            index = np.random.randint(len(population))
            r = np.random.uniform()

            parent = population[index]
            if r < parent.fitness:
                return parent

    for _ in range(runs):
        yield (sample(), sample())
    

def crossover_random(parent_1, parent_2):
    HALF = int(MAX_LIFE / 2)
    indices = [i for i in range(MAX_LIFE)]

    children = [Bird(), Bird()]
    for idx_1, idx_2 in zip(indices[HALF:], indices[:HALF]):
       children[0].genes[idx_1] = parent_1.genes[idx_1]
       children[0].genes[idx_2] = parent_2.genes[idx_2]
       children[1].genes[idx_1] = parent_2.genes[idx_1]
       children[1].genes[idx_2] = parent_1.genes[idx_2]

    return children


def crossover_half(parent_1, parent_2):
    HALF = int(MAX_LIFE / 2)
    
    children = [Bird(), Bird()]
    children[0].genes = parent_1.genes[:HALF] + parent_2.genes[HALF:]
    children[1].genes = parent_2.genes[:HALF] + parent_1.genes[:HALF]

    return children


def mutate(bird, rate):
    mutation = np.random.uniform(size=MAX_LIFE) < rate
    for i, mutate in enumerate(mutation):
        if mutate:
            stats['mutations'] += 1
            bird.genes[i] = generate_random_force()


game = Flappy()

ELITISM = True
MUTATION_RATE = 0.01

@game.register_ai
def super_ai(birds):
    new_population = []
    stats['mutations'] = 0

    if ELITISM:
        elite_bird = max(birds, key=lambda bird: bird.fitness)
        new_population.append(elite_bird)

    for parent_1, parent_2 in accept_reject(birds, runs=int(MAX_POPULATION / 2) - 10):
        # Crossover
        for child in crossover_random(parent_1, parent_2):
            # Mutation
            mutate(child, rate=MUTATION_RATE)

            # Add children to the new population
            new_population.append(child)
        
    print('Mutations:         ', stats['mutations'])
    print('Children created:  ', len(new_population) - 1)
    # Re-fill population
    d_pop = MAX_POPULATION - len(new_population)
    new_population += [Bird() for _ in range(d_pop)]
    print('Random birds added:', d_pop)
    print('New pop size:      ', len(new_population))
    print()
    return new_population

game.start()