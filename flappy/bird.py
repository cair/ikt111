from math import radians, sin, cos
from config import *
from utils import generate_random_angle_sequence, generate_random_force_vector

class Bird():
    def __init__(self):
        self.angle = generate_random_angle_sequence(MAX_LIFE)
        self.velocity = [generate_random_force_vector(angle) for angle in self.angle]
        self.alive = True

        #List of (angle,radius) pairs.
        self.rel_points = [[0, 20], [-140, 20], [180, 7.5], [140, 20]]
        scale = 0.5
        for i in range(len(self.rel_points)):
            self.rel_points[i] = (radians(self.rel_points[i][0]), scale * self.rel_points[i][1])

    def _reset_position(self):
        self.position = [0, HEIGHT]
        self.angle[0] = 135
        self.velocity[0] = generate_random_force_vector(self.angle[0])

    def _update(self, dt, i):
        """Helper function to update bird position and rotation"""
        self.position[0] += self.velocity[i][0] * dt
        self.position[1] += self.velocity[i][1] * dt

        # Check if out of bounds
        if self.position[0] < 0:
            self.alive = False
        elif self.position[0] > WIDTH:
            self.alive = False
        elif self.position[1] < 0:
            self.alive = False
        elif self.position[1] > HEIGHT:
            self.alive = False
        else:
            # It survives for now!
            pass

        self.real_points = []
        for point_angle, point_radius in self.rel_points:
            angle = radians(self.angle[i]) + point_angle
            xp = point_radius * sin(angle)
            yp = point_radius * cos(angle)
            self.real_points.append((
                self.position[0] + xp,
                self.position[1] + yp
            ))

    
    def _check_collide_obstacle(self, obstacles):
        """Helper function to check if bird collides with an obstacle"""
        for obstacle in obstacles:
            if self._check_collide_rect(obstacle.rect):
                self.alive = False
                break


    def _check_collide_goal(self, goal):
        """Helper function to check if bird reached goal"""
        if self._check_collide_rect(goal):
            self.alive = False
            return True
        return False            


    def _check_collide_rect(self, rect):
        """Helper function to check if a bird point is colliding with a rect"""
        for point in self.real_points:
            if rect.collidepoint(point):
                return True
        return False