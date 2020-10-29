from math import radians, sin, cos
from config import *
from utils import *

class Bird():
    def __init__(self):
        self.fitness = 0
        self.alive = True
        self.winner = False
        self.velocity = [0, 0]
        self.angle = START_ANGLE
        self.position = START_POS
        self.previous_position = START_POS
        self.genes = [generate_random_force() for _ in range(MAX_LIFE)]
        self._reset()

        self.focus = 0

        self.rel_points = calculate_rel_points()

    def _reset(self):
        """Helper function to reset the birds' position back to start"""
        self.fitness = 0
        self.focus = 0
        self.alive = True
        self.winner = False
        self.velocity = [0, 0]
        self.angle = START_ANGLE
        self.position = START_POS
        self.previous_position = START_POS
        
    def _update(self, dt, i):
        """Helper function to update bird position and rotation"""
        self.velocity[0] += self.genes[i][0]
        self.velocity[1] += self.genes[i][1]

        new_position = [self.position[0] + self.velocity[0] * dt,
                        self.position[1] + self.velocity[1] * dt]

        self.angle = self._calculate_new_angle(new_position)
        
        self.previous_position = self.position
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
        """Calculates the directional angle of the bird based on current velocity vector""" 
        d_x = new_position[0] - self.position[0]
        d_y = new_position[1] - self.position[1]
        return get_angle_between_points(d_x, d_y)

    def _check_collide_rect(self, rect):
        """Helper function to check if a bird point is colliding with a rect"""
        for point in self.real_points:
            if rect.collidepoint(point):
                return True
        return False


    def check_out_of_bounds(self):
        """This function checks if the bird has wandered off the game board
        
        If the bird is out-of-bounds, self.alive is set to False
        
        Returns:
            boolean: True if the bird is out-of-bounds, else False
        """
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
            return False
        return True


    def check_collide_obstacle(self, obstacles):
        """This function checks if the bird has collided with an obstacle

        If the bird has collided, self.alive is set to False

        Args:
            obstacles (list): List of obstacle Rect objects

        Returns:
            boolean: True if the bird has collided, else False
        """
        for obstacle in obstacles:
            if self._check_collide_rect(obstacle.rect):
                self.alive = False
                return True
        return False


    def check_collide_goal(self, goal):
        """ This function checks if the bird has reached the goal!

        If the bird has reached the goal:
            self.alive is set to False
            self.winner is set to True

        Args:
            goal (obj): goal Rect object

        Returns:
            boolean: True if the bird has reached the goal, else False

        """
        if self._check_collide_rect(goal):
            self.alive = False
            self.winner = True
            return True
        return False


    def calculate_fitness(self, goal_pos, score):
        """Improved fitness function"""
        euclidian_prev = calculate_euclidian_distance(self.previous_position, goal_pos)
        euclidian_current = calculate_euclidian_distance(self.position, goal_pos)


        # Preffer birds getting closer:
        fitness = (MAX_DIST - euclidian_current) ** 1.05
         
        # Update and add focus
        if euclidian_current < euclidian_prev:
            self.focus += 1
        else:
            self.focus -= 4

        self.fitness += self.focus

        if self.winner:
            # Reward fast birds:
            fitness += (MAX_LIFE - score) ** 1.08
        
        elif not self.alive:
            # If bird collided, punish!
            fitness = 0
        
        self.fitness = fitness
