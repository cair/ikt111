import math
import random
from functools import lru_cache

colors = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'black': (0, 0, 0),
    'gray': (100, 100, 100),
    'white': (255, 255, 255),
}

def generate_random_force():
    return [random.randint(-4, 4),
            random.randint(-4, 4)]


def get_angle_between_points(d_x, d_y):
    return math.atan2(d_x, d_y) * 180 / math.pi

@lru_cache(maxsize=10)
def calculate_rel_points(scale=0.5):
    # List of (angle,radius) pairs.
    rel_points = [[0, 20], [-140, 20], [180, 7.5], [140, 20]]
    for i in range(len(rel_points)):
        rel_points[i] = (math.radians(rel_points[i][0]), scale * rel_points[i][1])
    return rel_points


def calculate_euclidian_distance(bird_pos, goal_pos):
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(bird_pos, goal_pos)]))