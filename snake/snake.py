import random
import sys
import time 
import pygame
import numpy as np

import utils
import config

pygame.init()

colors = {
    'red':   (255, 0, 0),
    'green': (0, 255, 0),
    'blue':  (0, 0, 255),
    'black': (0, 0, 0),
    'gray':  (100, 100, 100),
    'white': (255, 255, 255),
}

class SnakeGame():
    def __init__(self):
        self.font_style = pygame.font.SysFont(None, 50)

        self.width   = config.WIDTH
        self.height  = config.HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake')

        self.clock = pygame.time.Clock()

        self.snake = None
        self.apple = None
        
        self.snake_delta_x = 0
        self.snake_delta_y = 0

        self.snake_len  = config.SNAKE_LEN
        self.snake_size = config.SNAKE_SIZE

        self.ai = lambda placeholder: self._game_over(msg='No AI registered!')


    def _display_message(self, msg, color=colors['blue']):
        message = self.font_style.render(msg, True, color)
        message_rect = message.get_rect(center=(self.width / 2, self.height / 2))

        self.display.blit(message, message_rect)
        pygame.display.update()
        time.sleep(1)


    def _load_image(self, img_path, colorkey=None):
        image = pygame.image.load(img_path).convert()
        image = pygame.transform.scale(image, (self.snake_size, self.snake_size))
        if colorkey:
            image.set_colorkey(colorkey)
        return image


    def _draw_snake(self):
        # Determine correct image for snake head
        snake_head = self.snake[-1]
        if snake_head[1] < self.snake[-2][1]:
            # Moving Up
            image = self._load_image('gfx/head_white.png')

        elif snake_head[0] > self.snake[-2][0]:
            # Moving right
            image = self._load_image('gfx/head_white.png')
            image = pygame.transform.rotate(image, 270)

        elif snake_head[1] > self.snake[-2][1]:
            # Moving down
            image = self._load_image('gfx/head_white.png')
            image = pygame.transform.rotate(image, 180)

        elif snake_head[0] < self.snake[-2][0]:
            # Moving left
            image = self._load_image('gfx/head_white.png')
            image = pygame.transform.rotate(image, 90)

        self.display.blit(image, snake_head)

        # Determine correct image for snake tail
        snake_tail = self.snake[0]
        if snake_tail[1] > self.snake[1][1]:
            # Moving Up
            image = self._load_image('gfx/tail_white.png')

        elif snake_tail[0] < self.snake[1][0]:
            # Moving right
            image = self._load_image('gfx/tail_white.png')
            image = pygame.transform.rotate(image, 270)

        elif snake_tail[1] < self.snake[1][1]:
            # Moving down
            image = self._load_image('gfx/tail_white.png')
            image = pygame.transform.rotate(image, 180)

        elif snake_tail[0] > self.snake[1][0]:
            # Moving left
            image = self._load_image('gfx/tail_white.png')
            image = pygame.transform.rotate(image, 90)

        self.display.blit(image, snake_tail)
        
        # Determine correct image for the body
        for i, seg in enumerate(self.snake[1:-1], 1):
            p_seg = self.snake[i + 1]
            n_seg = self.snake[i - 1]

            if (n_seg[0] < seg[0] and p_seg[0] > seg[0]) or \
            (p_seg[0] < seg[0] and n_seg[0] > seg[0]):
                # Horisontal segment
                image = self._load_image('gfx/straight.png')

            elif (n_seg[1] < seg[1] and p_seg[1] > seg[1]) or \
                (p_seg[1] < seg[1] and n_seg[1] > seg[1]):
                # Vertical segment
                image = self._load_image('gfx/straight.png')
                image = pygame.transform.rotate(image, 90)

            elif (n_seg[0] > seg[0] and p_seg[1] < seg[1]) or \
                (p_seg[0] > seg[0] and n_seg[1] < seg[1]):
                # Angle Left-Up
                image = self._load_image('gfx/bend_white.png')

            elif (n_seg[1] < seg[1] and p_seg[0] < seg[0]) or \
                (p_seg[1] < seg[1] and n_seg[0] < seg[0]):
                # Angle Top-Left
                image = self._load_image('gfx/bend_white.png')
                image = pygame.transform.rotate(image, 90)    

            elif (n_seg[0] < seg[0] and p_seg[1] > seg[1]) or \
                (p_seg[0] < seg[0] and n_seg[1] > seg[1]):
                # Angle Left-Down
                image = self._load_image('gfx/bend_white.png')
                image = pygame.transform.rotate(image, 180)

            elif (n_seg[1] > seg[1] and p_seg[0] > seg[0]) or \
                (p_seg[1] > seg[1] and n_seg[0] > seg[0]):
                # Angle Down-Right
                image = self._load_image('gfx/bend_white.png')
                image = pygame.transform.rotate(image, 270)

            else:
                # Failsafe - probably won't happen
                pygame.draw.rect(self.display, colors['green'], [seg[0], seg[1], self.snake_size, self.snake_size])
                return
            
            self.display.blit(image, seg)


    def _draw_apple(self):
        image = self._load_image('gfx/apple_white.png')
        self.display.blit(image, self.apple)


    def _update_display(self):
        self.display.fill(colors['white'])
        self._draw_apple()
        self._draw_snake()
        pygame.display.update()

    
    def _set_direction(self, direction):
        if direction == 'up' and self.snake_delta_y != self.snake_size:
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

    def _move_snake(self):
        snake_head = self.snake[-1].copy()
        snake_head[0] += self.snake_delta_x
        snake_head[1] += self.snake_delta_y
        self.snake.append(snake_head)

        if len(self.snake) > self.snake_len:
            del self.snake[0]


    def _check_quit_event(self, event):
        if event.type == pygame.QUIT:
            self._game_over(msg='Quitting...')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self._game_over(msg='Quitting...')


    def _check_move_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._set_direction('left')
            if event.key == pygame.K_RIGHT:
                self._set_direction('right')
            if event.key == pygame.K_UP:
                self._set_direction('up')
            if event.key == pygame.K_DOWN:
                self._set_direction('down')


    def _is_stationary(self):
        if self.snake_delta_x == 0 and self.snake_delta_y == 0:
            return True
        else:
            return False

    
    def _check_if_apple_eaten(self):
        # TODO: Implement next
        if self.snake[-1] == self.apple:
            self.apple = self._get_random_position()
            self.snake_len += 1


    def _check_collision_with_self(self):
        if self.snake_len > 1:
            for segment in self.snake[:-1]:
                if self.snake[-1] == segment:
                    self._game_over()


    def _check_out_of_bounds(self):
        snake_head = self.snake[-1]
        if snake_head[0] >= self.width or snake_head[0] < 0 or snake_head[1] >= self.height or snake_head[1] < 0:
            self._game_over()


    def _check_win_condition(self):
        # Check win condition
        if not 0 in self.get_game_state():
            self._game_won()


    def _get_random_position(self):
        if not self.snake and not self.apple:
            return [utils.rand_p(self.width), 
                    utils.rand_p(self.height)]
        
        legal_pos  = self._get_legal_position()
        return legal_pos


    def _get_legal_position(self):
        legal_positions = [p for p in zip(*np.where(self.get_game_state() == 0))]
        pos = random.choice(legal_positions)
        return [pos[0] * self.snake_size, 
                pos[1] * self.snake_size]


    def _game_over(self, msg='You Lost'):
        self._display_message(msg)
        self._exit()


    def _game_won(self, msg='You Won!'):
        self._display_message(msg)
        self._exit()


    def _exit(self):
        pygame.quit()
        quit()


    def get_game_state(self):
        SNAKE = 1
        APPLE = 2

        game_state = np.zeros((int(self.width / self.snake_size), 
                               int(self.height / self.snake_size)))
        
        if self.snake:
            for segment in self.snake:
                game_state[utils.pos_to_int(segment)] = SNAKE
        
        if self.apple:
            game_state[utils.pos_to_int(self.apple)] = APPLE

        return game_state


    def register_ai(self, f):
        self.ai = f


    def start(self, use_ai=False):
        self.snake = [[int(self.width / 2), 
                       int((self.height / 2)) + i * self.snake_size] 
                       for i in range(self.snake_len)]
        self.apple = self._get_random_position()
        self._update_display()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._game_over(msg='Quitting...')
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self._game_over(msg='Quitting...')
                        break
                    if event.key == pygame.K_LEFT and self.snake_delta_x != self.snake_size:
                        self.snake_delta_x = -self.snake_size
                        self.snake_delta_y = 0
                        break
                    if event.key == pygame.K_RIGHT and self.snake_delta_x != -self.snake_size:
                        self.snake_delta_x = self.snake_size
                        self.snake_delta_y = 0
                        break
                    if event.key == pygame.K_UP and self.snake_delta_y != self.snake_size and not self._is_stationary():
                        self.snake_delta_y = -self.snake_size
                        self.snake_delta_x = 0
                        break
                    if event.key == pygame.K_DOWN and self.snake_delta_y != -self.snake_size:
                        self.snake_delta_y = self.snake_size
                        self.snake_delta_x = 0
                        break

            if self._is_stationary():
                self.clock.tick(config.CLOCK_SPEED)
                continue
            
            self._move_snake()
            self._check_if_apple_eaten()
            self._check_out_of_bounds()
            self._check_collision_with_self()
            self._check_win_condition()
            
            self._update_display()
            self.clock.tick(config.CLOCK_SPEED)