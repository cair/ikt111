import numpy as np
import random
import config


def pos_to_int(pos):
    """Helper function that converts position values to integer"""
    return (int(pos[0] / config.SNAKE_SIZE), 
            int(pos[1] / config.SNAKE_SIZE))


def rand_p(_max):
    """Helper function to generate a random position value""" 
    return int(round(random.randrange(0, _max - config.SNAKE_SIZE) / config.SNAKE_SIZE) * config.SNAKE_SIZE)