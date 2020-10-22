import time
from math import radians, sin, cos
import random
import pygame
from utils import *
pygame.init()

WIDTH = 800
HEIGHT = 600
CLOCK_SPEED = 10

MAX_LIFE = 600

colors = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'black': (0, 0, 0),
    'gray': (100, 100, 100),
    'white': (255, 255, 255),
}

class Obstacle():
    def __init__(self, pos_x, pos_y):
        self.width = 160
        self.height = 250
        self.rect = pygame.Rect(pos_x, pos_y, self.width, self.height)
        self.color = colors['black']

class Player():
    def __init__(self):
        self.position = [0, HEIGHT]

        self.angle = 135#random.uniform(0, 360)

        self.angle = generate_random_angle_sequence(MAX_LIFE)
        self.velocity = [generate_random_force_vector(angle) for angle in self.angle]
        self.alive = True

        #List of (angle,radius) pairs.
        self.rel_points = [[0, 20], [-140, 20], [180, 7.5], [140, 20]]
        scale = 0.5
        for i in range(len(self.rel_points)):
            self.rel_points[i] = (radians(self.rel_points[i][0]), scale * self.rel_points[i][1])

    def update(self, dt, i):
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

class Birds:
    def __init__(self):
        self.font_style = pygame.font.SysFont(None, 80)
        self.width   = WIDTH
        self.height  = HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Evolutionary Birds')
        self.clock = pygame.time.Clock()

        self.obstacles = [
            Obstacle(0, 0),
            Obstacle(160 * 2, 350),
            Obstacle(160 * 4, 0)
        ]

        size = 50
        self.goal = pygame.Rect(WIDTH - size, HEIGHT - size, size, size)
        self.players = [Player() for _ in range(100)]
        self.ai = None

    def _update_display(self):
        """Helper function to update pygame display"""
        self.display.fill(colors['white'])

        for obstacle in self.obstacles:
            pygame.draw.rect(self.display,
                             (obstacle.color),
                             obstacle.rect)
        
        pygame.draw.rect(self.display,
                         colors['green'],
                         self.goal)

        for player in self.players:
            pygame.draw.aalines(self.display,
                                colors['black'],
                                True,
                                player.real_points,
                                True)

        pygame.display.update()


    def _display_message(self, msg, color=colors['blue']):
        """Helper function to show message on display"""
        message = self.font_style.render(msg, True, color)
        message_rect = message.get_rect(center=(self.width / 2, self.height / 2))

        self.display.blit(message, message_rect)
        pygame.display.update()
        time.sleep(1)


    def _exit(self):
        """Helper function to exit the game"""
        pygame.quit()
        quit()


    def _game_over(self, msg='You Lost'):
        """Helper function to display a loss-condition message"""
        self._display_message(msg)
        self._exit()


    def _game_won(self, msg='You Won!'):
        """Helper function to display a win-condition message"""
        self._display_message(msg)
        self._exit()


    def _check_quit_event(self, event):
        """Helper function to check for "user want's to quit" conditions"""
        if event.type == pygame.QUIT:
            self._game_over(msg='Quitting...')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self._game_over(msg='Quitting...')


    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f

    def start(self):
        target_fps = 60
        dt = 1.0/float(target_fps)
        
        # Start game loop
        counter = 0
        while True:
            for event in pygame.event.get():
                self._check_quit_event(event)


            # RANDOM PLAYER MOVEMENT
            for player in self.players:
                if not player.alive: continue
                player.update(dt, counter)

                # Check collision with obstacle
                for obstacle in self.obstacles:
                    for point in player.real_points:
                        if obstacle.rect.collidepoint(point):
                            player.alive = False
                            break
                    else:
                        continue
                    break

            self._update_display()
            self.clock.tick(target_fps)
            print(counter)
            counter += 1
            if counter == MAX_LIFE:
                self._game_over()