from math import radians, sin, cos
from config import *
from utils import *

class Bird():
    def __init__(self):
        self.fitness = 0
        self.alive = True
        self.velocity = [0, 0]
        self.angle = START_ANGLE
        self.position = START_POS
        self.genes = [generate_random_force() for _ in range(MAX_LIFE)]
        self._reset()

        self.rel_points = calculate_rel_points()

    def _reset(self):
        """Helper function to reset the birds' position back to start"""
        self.fitness = 0
        self.alive = True
        self.velocity = [0, 0]
        self.angle = START_ANGLE
        self.position = START_POS
        

    def _update(self, dt, i):
        """Helper function to update bird position and rotation"""
        self.velocity[0] += self.genes[i][0]
        self.velocity[1] += self.genes[i][1]

        new_position = [self.position[0] + self.velocity[0] * dt,
                        self.position[1] + self.velocity[1] * dt]

        self.angle = self._calculate_new_angle(new_position)
        
        self.position = new_position

        self.real_points = []
        for point_angle, point_radius in self.rel_points:
            angle = radians(self.angle) + point_angle
            xp = point_radius * sin(angle)
            yp = point_radius * cos(angle)
            self.real_points.append((
                self.position[0] + xp,
                self.position[1] + yp
            ))


    def _calculate_new_angle(self, new_position):
        d_x = new_position[0] - self.position[0]
        d_y = new_position[1] - self.position[1]
        return get_angle_between_points(d_x, d_y)


    def _check_out_of_bounds(self):
        """Helper function to check if bird tries to leave the game"""
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


    def calculate_fitness(self, goal_position):
        """Calculates fitness based on distance to goal and time alive ( Lower is better )"""
        self.fitness = calculate_euclidian_distance(self.position, goal_position)