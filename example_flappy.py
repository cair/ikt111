from ikt111_games.flappy import Bird
from ikt111_games import Flappy
import random

# This determines both the bird lifespan
# and how many genes they have
MAX_LIFE = 1000

# This sets the maximum population size
MAX_POPULATION = 100

# Initialize the environment with a set MAX_LIFE and MAX_POPULATION
environment = Flappy(max_life=MAX_LIFE, max_population=MAX_POPULATION)


def generate_random_force(_min=-4, _max=4):
    """Generate a random force vector with x and y in the interval [_min, _max]

    Args:
        _min (int): Highest force in negative directions. Defaults to -4
        _max (int): Highest force in positive directions. Defaults to 4

    Returns:
        list: Force vector
    """
    return [random.randint(_min, _max), random.randint(_min, _max)]


# Probably some code/functions that can be implemented here


@environment.register_ai
def super_ai(birds):
    """A super AI function!"""

    # Do some AI magic here, instead of just returning the same birds

    return birds


environment.start()
