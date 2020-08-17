import numpy as np
import random
import config

def rand_p(_max):
    return int(round(random.randrange(0, _max - config.SNAKE_SIZE) / config.SNAKE_SIZE) * config.SNAKE_SIZE)


def get_random_position(snake=None, apple=None):
    if not snake and not apple:
        return (rand_p(config.WIDTH), rand_p(config.HEIGHT))
    
    game_state = get_game_state(snake, apple)
    legal_pos  = get_legal_position(game_state)
    return legal_pos


def pos_to_int(pos):
    return (int(pos[0] / config.SNAKE_SIZE), 
            int(pos[1] / config.SNAKE_SIZE))


def get_legal_position(game_state):
    legal_positions = [p for p in zip(*np.where(game_state == 0))]
    pos = random.choice(legal_positions)
    return [pos[0] * config.SNAKE_SIZE, pos[1] * config.SNAKE_SIZE]



def get_game_state(snake=None, apple=None):
    SNAKE = 1
    APPLE = 2

    game_state = np.zeros((int(config.WIDTH / config.SNAKE_SIZE), 
                           int(config.HEIGHT / config.SNAKE_SIZE)))
    
    if snake:
        for segment in snake:
            game_state[pos_to_int(segment)] = SNAKE
    
    if apple:
        game_state[pos_to_int(apple)] = APPLE

    return game_state


def is_stationary(x_d, y_d):
    if x_d == 0 and y_d == 0:
        return True
    else:
        return False