import random
import sys
import time 
import pygame
import numpy as np

import utils
import config

colors = {
    'red':   (255, 0, 0),
    'green': (0, 255, 0),
    'blue':  (0, 0, 255),
    'black': (0, 0, 0),
    'gray':  (100, 100, 100),
    'white': (255, 255, 255),
}

pygame.init()
font_style = pygame.font.SysFont(None, 50)

def message(msg, color):
    global display

    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [config.WIDTH / 2.4, config.HEIGHT / 2.4])

display = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption('Snake')

game_over = False

clock = pygame.time.Clock()


def load_image(img_path, colorkey=None):
    image = pygame.image.load(img_path).convert()
    image = pygame.transform.scale(image, (config.SNAKE_SIZE, config.SNAKE_SIZE))
    if colorkey:
        image.set_colorkey(colorkey)
    return image

def draw_snake(snake):
    # Determine correct image for snake head
    snake_head = snake[-1]
    if snake_head[1] < snake[-2][1]:
        # Moving Up
        image = load_image('gfx/head_white.png')

    elif snake_head[0] > snake[-2][0]:
        # Moving right
        image = load_image('gfx/head_white.png')
        image = pygame.transform.rotate(image, 270)

    elif snake_head[1] > snake[-2][1]:
        # Moving down
        image = load_image('gfx/head_white.png')
        image = pygame.transform.rotate(image, 180)

    elif snake_head[0] < snake[-2][0]:
        # Moving left
        image = load_image('gfx/head_white.png')
        image = pygame.transform.rotate(image, 90)

    display.blit(image, snake_head)

    # Determine correct image for snake tail
    snake_tail = snake[0]
    if snake_tail[1] > snake[1][1]:
        # Moving Up
        image = load_image('gfx/tail_white.png')

    elif snake_tail[0] < snake[1][0]:
        # Moving right
        image = load_image('gfx/tail_white.png')
        image = pygame.transform.rotate(image, 270)

    elif snake_tail[1] < snake[1][1]:
        # Moving down
        image = load_image('gfx/tail_white.png')
        image = pygame.transform.rotate(image, 180)

    elif snake_tail[0] > snake[1][0]:
        # Moving left
        image = load_image('gfx/tail_white.png')
        image = pygame.transform.rotate(image, 90)

    display.blit(image, snake_tail)
    
    # Determine correct image for the body
    for i, seg in enumerate(snake[1:-1], 1):
        p_seg = snake[i + 1]
        n_seg = snake[i - 1]

        if (n_seg[0] < seg[0] and p_seg[0] > seg[0]) or \
           (p_seg[0] < seg[0] and n_seg[0] > seg[0]):
            # Horisontal segment
            image = load_image('gfx/straight.png')

        elif (n_seg[1] < seg[1] and p_seg[1] > seg[1]) or \
             (p_seg[1] < seg[1] and n_seg[1] > seg[1]):
            # Vertical segment
            image = load_image('gfx/straight.png')
            image = pygame.transform.rotate(image, 90)

        elif (n_seg[0] > seg[0] and p_seg[1] < seg[1]) or \
             (p_seg[0] > seg[0] and n_seg[1] < seg[1]):
            # Angle Left-Up
            image = load_image('gfx/bend_white.png')

        elif (n_seg[1] < seg[1] and p_seg[0] < seg[0]) or \
             (p_seg[1] < seg[1] and n_seg[0] < seg[0]):
            # Angle Top-Left
            image = load_image('gfx/bend_white.png')
            image = pygame.transform.rotate(image, 90)    

        elif (n_seg[0] < seg[0] and p_seg[1] > seg[1]) or \
             (p_seg[0] < seg[0] and n_seg[1] > seg[1]):
            # Angle Left-Down
            image = load_image('gfx/bend_white.png')
            image = pygame.transform.rotate(image, 180)

        elif (n_seg[1] > seg[1] and p_seg[0] > seg[0]) or \
             (p_seg[1] > seg[1] and n_seg[0] > seg[0]):
            # Angle Down-Right
            image = load_image('gfx/bend_white.png')
            image = pygame.transform.rotate(image, 270)

        else:
            # Failsafe - probably won't happen
            pygame.draw.rect(display, colors['green'], [seg[0], seg[1], config.SNAKE_SIZE, config.SNAKE_SIZE])
            return
        
        display.blit(image, seg)

def draw_apple(pos):
    image = load_image('gfx/apple_white.png')
    display.blit(image, pos)


def update_display(snake, apple):
    display.fill(colors['white'])
    draw_apple(apple)
    draw_snake(snake)
    pygame.display.update()


def game_loop(use_ai=False):
    game_over = False
    msg = 'You lost'

    x_delta = 0
    y_delta = 0

    snake_len = 3
    snake_list = [[int(config.WIDTH / 2), int((config.HEIGHT / 2)) + i * config.SNAKE_SIZE] 
                  for i in range(snake_len)]

    apple = utils.get_random_position(snake=snake_list)

    update_display(snake_list, apple)

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True
                    break
                if event.key == pygame.K_LEFT and x_delta != config.SNAKE_SIZE:
                    x_delta = -config.SNAKE_SIZE
                    y_delta = 0
                    break
                if event.key == pygame.K_RIGHT and x_delta != -config.SNAKE_SIZE:
                    x_delta = config.SNAKE_SIZE
                    y_delta = 0
                    break
                if event.key == pygame.K_UP and y_delta != config.SNAKE_SIZE and not utils.is_stationary(x_delta, y_delta):
                    y_delta = -config.SNAKE_SIZE
                    x_delta = 0
                    break
                if event.key == pygame.K_DOWN and y_delta != -config.SNAKE_SIZE:
                    y_delta = config.SNAKE_SIZE
                    x_delta = 0
                    break

        if utils.is_stationary(x_delta, y_delta):
            clock.tick(config.CLOCK_SPEED)
            continue
        
        # Move the snake by creating a 'new head'
        # at the new position
        x, y = snake_list[-1]
        x += x_delta
        y += y_delta
        snake_list.append([x, y])

        if len(snake_list) > snake_len:
            del snake_list[0]

        # Check if snake is outside the game board
        if x >= config.WIDTH or x < 0 or y >= config.HEIGHT or y < 0:
            break

        # Check win condition
        game_state = utils.get_game_state(snake_list, apple)
        if not 0 in game_state:
            msg = 'You won!'
            break

        # Check if snake has eaten the apple
        # Don't remove the tail-end if true to allow growth
        if x == apple[0] and y == apple[1]:
            apple = utils.get_random_position(snake=snake_list)
            snake_len += 1


        # Check if snake has collided with itself:
        if len(snake_list) > 1:
            for x_body, y_body in snake_list[:-1]:
                if x == x_body and y == y_body:
                    game_over = True

        if not game_over:
            update_display(snake_list, apple)

            clock.tick(config.CLOCK_SPEED)

    message(msg, colors['blue'])
    pygame.display.update()
    time.sleep(1)

    pygame.quit()
    quit()

if __name__ == '__main__':
    game_loop()