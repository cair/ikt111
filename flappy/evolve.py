import random
import numpy as np
from itertools import zip_longest
from bird import Bird
from flappy import Flappy
from config import *
from utils import generate_random_force

game = Flappy()

ELITISM = True
MUTATION_RATE = 0.01

stats = {
    'mutations': 0
}


def accept_reject(population, runs):
    max_fitness = max(population, key=lambda bird: bird.fitness).fitness
    for bird in population:
        try:
            bird.fitness /= max_fitness
        except ZeroDivisionError:
            bird.fitness = random.random()

    def sample():
        while True:
            index = np.random.randint(len(population))
            r = np.random.uniform()

            parent = population[index]
            if r < parent.fitness:
                return parent

    for _ in range(runs):
        yield (sample(), sample())
    

def crossover(parent_1, parent_2):
    HALF = int(MAX_LIFE / 2)
    indices = [i for i in range(MAX_LIFE)]
    random.shuffle(indices)

    children = [Bird(), Bird()]
    for idx_1, idx_2 in zip(indices[HALF:], indices[:HALF]):
       children[0].genes[idx_1] = parent_1.genes[idx_1]
       children[0].genes[idx_2] = parent_2.genes[idx_2]
       children[1].genes[idx_1] = parent_2.genes[idx_1]
       children[1].genes[idx_2] = parent_1.genes[idx_2]

    return children


def mutate(bird, rate):
    mutation = np.random.uniform(size=MAX_LIFE) < rate
    for i, mutate in enumerate(mutation):
        if mutate:
            stats['mutations'] += 1
            bird.genes[i] = generate_random_force()


@game.register_ai
def super_ai(birds):
    new_population = []
    stats['mutations'] = 0

    if ELITISM:
        elite_bird = max(birds, key=lambda bird: bird.fitness)
        new_population.append(elite_bird)

    for parent_1, parent_2 in accept_reject(birds, runs=int(MAX_POPULATION / 2) - 10):
        # Crossover
        for child in crossover(parent_1, parent_2):
            # Mutation
            mutate(child, rate=MUTATION_RATE)

            # Add children to the new population
            new_population.append(child)
        

    # Re-fill population
    d_pop = MAX_POPULATION - len(new_population)
    new_population += [Bird() for _ in range(d_pop)]
    
    print('Mutations:         ', stats['mutations'])
    print()
    
    return new_population

game.start()