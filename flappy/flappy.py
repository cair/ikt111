import math
import time
import random
import pygame
from config import *
from utils import colors
from bird import Bird
pygame.init()


class Obstacle():
    def __init__(self, pos_x, pos_y):
        self.width = 160
        self.height = 250
        self.rect = pygame.Rect(pos_x, pos_y, self.width, self.height)
        self.color = colors['black']


class Flappy:
    def __init__(self):
        self.messages_font = pygame.font.SysFont(None, 80)
        self.stats_font = pygame.font.SysFont(None, 26)
        self.width   = WIDTH
        self.height  = HEIGHT + STATS_HEIGHT
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
        self.goal_position = self.goal.center
        self.birds = []

        self.stats = {}

        self.ai = None

    def _update_display(self):
        """Helper function to update pygame display"""
        # Fill background white first...
        self.display.fill(colors['white'])

        # ... Then fill stats-area black and draw them
        self.display.fill(colors['black'], (0, HEIGHT, WIDTH, STATS_HEIGHT))
        self._display_stats()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(self.display,
                             (obstacle.color),
                             obstacle.rect)
        
        # Draw goal
        pygame.draw.rect(self.display,
                         colors['green'],
                         self.goal)

        # Draw birds
        for bird in self.birds:
            pygame.draw.aalines(self.display,
                                colors['black'],
                                True,
                                bird.real_points,
                                True)

        # Draw best, alive bird in another color
        self.birds.sort(key=lambda bird: bird.fitness, reverse=True)
        try:
            bird = next(b for b in self.birds if b.alive)
        except StopIteration:
            pass
        else:
            pygame.draw.aalines(self.display,
                                colors['red'],
                                True,
                                bird.real_points,
                                True)
        pygame.display.update()


    def _display_message(self, msg, color=colors['blue']):
        """Helper function to show message on display"""
        message = self.messages_font.render(msg, True, color)
        message_rect = message.get_rect(center=(self.width / 2, self.height / 2))

        self.display.blit(message, message_rect)
        pygame.display.update()
        time.sleep(1)


    def _display_stats(self):
        """Helper function to draw stats on the screen"""    
        color = colors['white']
        elements = []

        # Generation
        text = self.stats_font.render(f'Generation: {self.stats["generation"]}', True, color)
        text_rect = text.get_rect(left=20, top=HEIGHT + 20)
        elements.append((text, text_rect))

        # Lifespan
        text = self.stats_font.render(f'Lifespan: {self.stats["lifespan"]}', True, color)
        text_rect = text.get_rect(left=20, top=HEIGHT + 50)
        elements.append((text, text_rect))

        text = self.stats_font.render(f'/ {MAX_LIFE}', True, color)
        text_rect = text.get_rect(left=130 if self.stats['lifespan'] < 100 else 137,
                                  top=HEIGHT + 50)
        elements.append((text, text_rect))

        num_winners = 0
        num_dead = 0
        for bird in self.birds:
            if not bird.alive:
                if bird.winner:
                    num_winners += 1
                else:
                    num_dead += 1
        # Birds alive
        text = self.stats_font.render(f'Birds alive: {len(self.birds) - (num_dead + num_winners)}', True, color)
        text_rect = text.get_rect(left=250, top=HEIGHT + 20)
        elements.append((text, text_rect))

        # Birds dead
        text = self.stats_font.render(f'Birds dead: {num_dead}', True, color)
        text_rect = text.get_rect(left=250, top=HEIGHT + 50)
        elements.append((text, text_rect))

        # Winners
        text = self.stats_font.render(f'Winners: {num_winners}', True, color)
        text_rect = text.get_rect(left=250, top=HEIGHT + 80)
        elements.append((text, text_rect))
        
        # Best fitness
        text = self.stats_font.render(f'Best fitness: {self.stats["best_fitness"]:.0f}', True, color)
        text_rect = text.get_rect(left=480, top=HEIGHT + 20)
        elements.append((text, text_rect))

        # Avg. fitness
        text = self.stats_font.render(f'Average fitness: {self.stats["mean_fitness"]:.0f}', True, color)
        text_rect = text.get_rect(left=480, top=HEIGHT + 50)
        elements.append((text, text_rect))

        # FPS
        text = self.stats_font.render(f'FPS: {self.clock.get_fps():.0f}', True, color)
        text_rect = text.get_rect(left=WIDTH - 80, top=HEIGHT + STATS_HEIGHT - 30)
        elements.append((text, text_rect))

        for element in elements:
            self.display.blit(*element)


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

    
    def _generate_initial_population(self):
        """Helper function to generate the initial population of birds"""
        return [Bird() for _ in range(MAX_POPULATION)]
            

    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f


    def start(self):
        target_fps = 60
        dt = 1.0/float(target_fps)
        
        # Create initial population
        self.birds = self._generate_initial_population()

        # Start game loop
        self.stats['generation'] = 1
        while True:

            # Simulate population
            self.stats['lifespan'] = 0
            while self.stats['lifespan'] < MAX_LIFE:
                # Process user input
                for event in pygame.event.get():
                    self._check_quit_event(event)

                # Process birds
                for bird in self.birds:
                    if not bird.alive: continue 
                    bird._update(dt, self.stats['lifespan'])
                    bird._check_out_of_bounds()
                    bird._check_collide_obstacle(self.obstacles)
                    bird._check_collide_goal(self.goal)
                    bird.calculate_fitness(self.goal_position, self.stats['lifespan'])

                self.stats['best_fitness'] = max(self.birds, key=lambda bird: bird.fitness).fitness
                self.stats['mean_fitness'] = sum([bird.fitness for bird in self.birds]) / len(self.birds)

                self._update_display()
                self.clock.tick(target_fps)

                self.stats['lifespan'] += 1

            # Simulation done - hand-off to Darwin
            time.sleep(1)
            self.birds = self.ai(self.birds)
            self.birds = self.birds[:MAX_POPULATION]

            # Check for correct type
            if not isinstance(self.birds, list):
                print(f'Algorithm did not return a list! Got \'{type(self.birds)}\' instead')
                self._game_over('Error!')

            # Stop game if algorithm returns an empty array
            if not self.birds:
                print('Algorithm returned an empty population!')
                self._game_over('Error!')

            # Reset all birds' first position so they start with the correct angle
            for bird in self.birds:
                bird._reset()

            self.stats['generation'] += 1