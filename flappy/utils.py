import math
import random

colors = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'black': (0, 0, 0),
    'gray': (100, 100, 100),
    'white': (255, 255, 255),
}

def generate_random_force_vector(angle):
    force = random.uniform(50, 150)
    return [force * math.sin(math.radians(angle)),
            force * math.cos(math.radians(angle))]

def generate_random_angle_sequence(n):
    angles = [135]
    for i in range(1, n):
        delta = random.randint(-4, 4)
        angles.append(angles[i - 1] + delta)
    return angles
