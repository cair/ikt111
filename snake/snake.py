import random
import sys
import time
import pygame
import numpy as np
import copy

import utils
import config

pygame.init()

colors = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'black': (0, 0, 0),
    'gray': (100, 100, 100),
    'white': (255, 255, 255),
}

states = {
    'board': 0,
    'snake_body': 1,
    'snake_head': 2,
    'apple': 3
}


class SnakeGame:
    def __init__(self):
        self.font_style = pygame.font.SysFont(None, 50)

        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake')

        self.clock = pygame.time.Clock()

        self.snake = None
        self.apple = None

        self.snake_delta_x = 0
        self.snake_delta_y = 0

        self.snake_len = config.SNAKE_LEN
        self.snake_size = config.SNAKE_SIZE

        self.sprites = {
            'apple': pygame.image.load('gfx/apple.png').convert_alpha(),
            'bend': pygame.image.load('gfx/bend.png').convert_alpha(),
            'head': pygame.image.load('gfx/head.png').convert_alpha(),
            'straight': pygame.image.load('gfx/straight.png').convert_alpha(),
            'tail': pygame.image.load('gfx/tail.png').convert_alpha()
        }

        self.game_state = None
        self.moves = []
        self.ai = lambda placeholder: self._game_over(msg='No AI registered!')

    def _display_message(self, msg, color=colors['blue']):
        """Helper function to show message on display"""
        message = self.font_style.render(msg, True, color)
        message_rect = message.get_rect(
            center=(self.width / 2, self.height / 2))

        self.display.blit(message, message_rect)
        pygame.display.update()
        time.sleep(1)

    def _load_image(self, sprite_name, color_key=None):
        """Helper function to load image from disk"""
        image = self.sprites[sprite_name]
        image = pygame.transform.scale(image,
                                       (self.snake_size, self.snake_size))
        if color_key:
            image.set_colorkey(color_key)
        return image

    def _draw_snake(self):
        """Helper function to draw snake on display"""
        # Determine correct image for snake head
        snake_head = self.snake[-1]
        if snake_head[1] < self.snake[-2][1]:
            # Moving Up
            image = self._load_image('head')

        elif snake_head[0] > self.snake[-2][0]:
            # Moving right
            image = self._load_image('head')
            image = pygame.transform.rotate(image, 270)

        elif snake_head[1] > self.snake[-2][1]:
            # Moving down
            image = self._load_image('head')
            image = pygame.transform.rotate(image, 180)

        elif snake_head[0] < self.snake[-2][0]:
            # Moving left
            image = self._load_image('head')
            image = pygame.transform.rotate(image, 90)

        self.display.blit(image, snake_head)

        # Determine correct image for snake tail
        snake_tail = self.snake[0]
        if snake_tail[1] > self.snake[1][1]:
            # Moving Up
            image = self._load_image('tail')

        elif snake_tail[0] < self.snake[1][0]:
            # Moving right
            image = self._load_image('tail')
            image = pygame.transform.rotate(image, 270)

        elif snake_tail[1] < self.snake[1][1]:
            # Moving down
            image = self._load_image('tail')
            image = pygame.transform.rotate(image, 180)

        elif snake_tail[0] > self.snake[1][0]:
            # Moving left
            image = self._load_image('tail')
            image = pygame.transform.rotate(image, 90)

        self.display.blit(image, snake_tail)

        # Determine correct image for the body
        for i, seg in enumerate(self.snake[1:-1], 1):
            p_seg = self.snake[i + 1]
            n_seg = self.snake[i - 1]

            if n_seg[0] < seg[0] < p_seg[0] or p_seg[0] < seg[0] < n_seg[0]:
                # Horizontal segment
                image = self._load_image('straight')

            elif n_seg[1] < seg[1] < p_seg[1] or p_seg[1] < seg[1] < n_seg[1]:
                # Vertical segment
                image = self._load_image('straight')
                image = pygame.transform.rotate(image, 90)

            elif (n_seg[0] > seg[0] and p_seg[1] < seg[1]) or \
                    (p_seg[0] > seg[0] and n_seg[1] < seg[1]):
                # Angle Left-Up
                image = self._load_image('bend')

            elif (n_seg[1] < seg[1] and p_seg[0] < seg[0]) or \
                    (p_seg[1] < seg[1] and n_seg[0] < seg[0]):
                # Angle Top-Left
                image = self._load_image('bend')
                image = pygame.transform.rotate(image, 90)

            elif (n_seg[0] < seg[0] and p_seg[1] > seg[1]) or \
                    (p_seg[0] < seg[0] and n_seg[1] > seg[1]):
                # Angle Left-Down
                image = self._load_image('bend')
                image = pygame.transform.rotate(image, 180)

            elif (n_seg[1] > seg[1] and p_seg[0] > seg[0]) or \
                    (p_seg[1] > seg[1] and n_seg[0] > seg[0]):
                # Angle Down-Right
                image = self._load_image('bend')
                image = pygame.transform.rotate(image, 270)

            else:
                # Failsafe - probably won't happen
                pygame.draw.rect(self.display, colors['green'],
                                 [seg[0], seg[1], self.snake_size,
                                  self.snake_size])
                return

            self.display.blit(image, seg)

    def _draw_apple(self):
        """Helper function to draw apple on display"""
        image = self._load_image('apple')
        self.display.blit(image, self.apple)

    def _update_display(self):
        """Helper function to update pygame display"""
        self.display.fill(colors['white'])
        self._draw_apple()
        self._draw_snake()
        pygame.display.update()

    def _set_direction(self, direction):
        """Helper function to set snake direction delta"""
        if direction == 'up' and self.snake_delta_y != self.snake_size and \
                not self._is_stationary():
            self.snake_delta_y = -self.snake_size
            self.snake_delta_x = 0
        elif direction == 'down' and self.snake_delta_y != -self.snake_size:
            self.snake_delta_y = self.snake_size
            self.snake_delta_x = 0
        elif direction == 'left' and self.snake_delta_x != self.snake_size:
            self.snake_delta_x = -self.snake_size
            self.snake_delta_y = 0
        elif direction == 'right' and self.snake_delta_x != -self.snake_size:
            self.snake_delta_x = self.snake_size
            self.snake_delta_y = 0
        else:
            # Unknown move - do nothing
            pass

    def _is_stationary(self):
        """Helper function to check if snake is standing still"""
        if self.snake_delta_x == 0 and self.snake_delta_y == 0:
            return True
        else:
            return False

    def _move_snake(self):
        """Helper function to move snake position"""
        snake_head = copy.deepcopy(self.snake[-1])
        snake_head[0] += self.snake_delta_x
        snake_head[1] += self.snake_delta_y
        self.snake.append(snake_head)

        if len(self.snake) > self.snake_len:
            del self.snake[0]

    def _check_move_event(self, event):
        """Helper function to extract move from user keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._set_direction('left')
            if event.key == pygame.K_RIGHT:
                self._set_direction('right')
            if event.key == pygame.K_UP:
                self._set_direction('up')
            if event.key == pygame.K_DOWN:
                self._set_direction('down')

    def _check_quit_event(self, event):
        """Helper function to check for "user want's to quit" conditions"""
        if event.type == pygame.QUIT:
            self._game_over(msg='Quitting...')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self._game_over(msg='Quitting...')

    def _check_if_apple_eaten(self):
        """Helper function to check if snake has eaten the apple"""
        if self.snake[-1] == self.apple:
            self.apple = self._get_random_position()
            self.snake_len += 1

    def _check_collision_with_self(self):
        """Helper function to check if snake has eaten itself"""
        if self.snake_len > 1 and self.snake[-1] in self.snake[:-1]:
            self._game_over()

    def _check_out_of_bounds(self):
        """Helper function to check if snake has moved outside the board"""
        snake_head = self.snake[-1]
        if snake_head[0] >= self.width or snake_head[0] < 0 or snake_head[
            1] >= self.height or snake_head[1] < 0:
            self._game_over()

    def _check_win_condition(self):
        """Helper function to check for win-conditions"""
        # Check win condition
        if 0 not in self.game_state:
            self._game_won()

    def _get_random_position(self):
        """Helper function to generate a random, legal position"""
        if not self.snake and not self.apple:
            return [utils.rand_p(self.width),
                    utils.rand_p(self.height)]

        legal_positions = self._get_legal_positions()
        pos = random.choice(legal_positions)
        return [pos[0] * self.snake_size,
                pos[1] * self.snake_size]

    def _get_legal_positions(self):
        """Helper function to get all current legal positions"""
        return np.array([p for p in zip(*np.where(self.game_state == 0))])

    def _game_over(self, msg='You Lost'):
        """Helper function to display a loss-condition message"""
        self._display_message(msg)
        self._exit()

    def _game_won(self, msg='You Won!'):
        """Helper function to display a win-condition message"""
        self._display_message(msg)
        self._exit()

    def _exit(self):
        """Helper function to exit the game"""
        pygame.quit()
        quit()

    def _update_game_state(self):
        """Converts the game canvas into a 2D numpy representation and
        updates the game state

        Possible game states:
            0: Empty location
            1: Snake body segment
            2: Snake head segment
            3: Apple
        """
        self.game_state = np.zeros((int(self.width / self.snake_size),
                                    int(self.height / self.snake_size)))

        if self.snake:
            self.game_state[utils.pos_to_int(self.snake[-1])] = states['snake_head']
            for segment in self.snake[:-1]:
                self.game_state[utils.pos_to_int(segment)] = states['snake_body']

        if self.apple:
            self.game_state[utils.pos_to_int(self.apple)] = states['apple']

    def is_legal(self, moves):
        """Function to check if a sequence of moves is legal / will not end
        in a loss-condition

        This function will simulate moving the snake according to the
        provided sequence of moves.

        Returns:
            bool: True if all the moves are legal
            bool: False if any of the moves end in a loss-condition
        """
        temp_snake = copy.deepcopy(self.snake)

        if isinstance(moves, str):
            moves = [moves]

        for move in moves:
            temp_head = copy.deepcopy(temp_snake[-1])
            
            if move == 'up':
                temp_head[1] += -self.snake_size
            elif move == 'down':
                temp_head[1] += self.snake_size
            elif move == 'left':
                temp_head[0] += -self.snake_size
            elif move == 'right':
                temp_head[0] += self.snake_size
            else:
                # Illegal move?
                return False

            # Out of bounds
            if (temp_head[0] < 0 or temp_head[0] >= self.width) or \
               (temp_head[1] < 0 or temp_head[1] >= self.height):
                return False

            # Collision with self
            # if self.snake_len > 1 and temp_head in self.snake[:-1]:
            if temp_head in temp_snake[:-1]:
                return False

            # Simulate move by updating temp_snake
            temp_snake.append(temp_head)
            del temp_snake[0]

        return True

    def is_winning(self, moves):
        """Function to check if a sequence of moves lead to the apple

        NB! This function will not check for legal moves

        Returns:
            bool: True if the sequence lead to the apple
            bool: False if the sequence does not lead to the apple
        """
        temp_snake = copy.deepcopy(self.snake)
        temp_head = temp_snake[-1]

        if isinstance(moves, str):
            moves = [moves]

        for move in moves:
            
            if move == 'up':
                temp_head[1] += -self.snake_size
            elif move == 'down':
                temp_head[1] += self.snake_size
            elif move == 'left':
                temp_head[0] += -self.snake_size
            elif move == 'right':
                temp_head[0] += self.snake_size
            else:
                # Illegal move?
                return False

            if temp_head[0] == self.apple[0] and temp_head[1] == self.apple[1]:
                return True

        return False

    def get_game_state(self):
        """The game state is a 2D numpy representation of the game canvas and
           contains relevant game information states in numeric form:

        Possible game states:
            0: Empty location
            1: Snake body segment
            2: Snake head segment
            3: Apple
        """
        return self.game_state

    def get_snake_head_position(self):
        """Returns the current position og the snake head in the game state"""
        pos = np.where(self.game_state == states['snake_head'])
        return list(np.hstack(pos))

    def get_apple_position(self):
        """Returns the current position of the apple in the game state"""
        pos = np.where(self.game_state == states['apple'])
        return list(np.hstack(pos))

    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f

    def start(self, use_ai=False):
        self.update_game_state()
        self.snake = [[int(self.width / 2),
                       int((self.height / 2)) + i * self.snake_size]
                      for i in range(self.snake_len)]
        self.apple = self._get_random_position()
        self.update_game_state()
        self._update_display()

        # Game Loop
        while True:
            for event in pygame.event.get():
                self._check_quit_event(event)

                if not use_ai:
                    self._check_move_event(event)

            if use_ai:
                if not self.moves:
                    new_moves = self.ai()
                    if not new_moves:
                        self._game_over()
                    self.moves = self.ai()
                direction = self.moves.pop(0)
                self._set_direction(direction)

            if self._is_stationary():
                self.clock.tick(config.CLOCK_SPEED)
                continue

            self._move_snake()
            self.update_game_state()
            self._check_if_apple_eaten()
            self.update_game_state()
            self._check_out_of_bounds()
            self._check_collision_with_self()
            self._check_win_condition()

            self.update_game_state()
            self._update_display()
            self.clock.tick(config.CLOCK_SPEED)