import math
import random

def generate_random_force_vector(angle):
    force = random.uniform(50, 150)
    return [force * math.sin(math.radians(angle)),
            force * math.cos(math.radians(angle))]

def generate_random_angle_sequence(n, start=135):
    angles = [135]
    for i in range(1, n):
        delta = random.randint(-4, 4)
        angles.append(angles[i - 1] + delta)
    return angles
