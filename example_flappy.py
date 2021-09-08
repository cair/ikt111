from ikt111_games.flappy.bird import Bird
from ikt111_games import Flappy
import random

# This determines both the bird lifespan
# and how many genes they have
MAX_LIFE = 1000

# This sets the maximum population size
MAX_POPULATION = 10


def generate_random_force(_min=-4, _max=4):
    """Generate a random force vector with x and y in the interval [_min, _max]

    Args:
        _min (int): Highest force in negative directions. Defaults to -4
        _max (int): Highest force in positive directions. Defaults to 4

    Returns:
        list: Force vector
    """
    return [random.randint(_min, _max), random.randint(_min, _max)]


game = Flappy(max_life=MAX_LIFE, max_population=MAX_POPULATION)


@game.register_ai
def super_ai(birds):
    """A super AI function!

    There is a 33% chance that:
        1. A bird is replaced by a new, randomly generated one!
        2. A bird has a random gene swapped with a new, randomly generated one!
        3. A bird survives, without changes.
    """

    # Loop through the index of all birds
    for i in range(len(birds)):

        # Generate a random float in the interval [0, 1)
        r = random.random()
        if r < 0.33:
            # Replace birds[i] with a new, random bird
            birds[i] = Bird(max_life=MAX_LIFE)

        elif r < 0.66:
            # Generate a random integer in the interval [0, MAX_LIFE - 1]
            r_i = random.randint(0, MAX_LIFE - 1)

            # Replace a random gene in bird[i] with a new, random force vector
            birds[i].genes[r_i] = generate_random_force()

        else:
            # Don't do anything!
            pass

    return birds


game.start()
