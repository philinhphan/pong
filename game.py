import asyncio
import pygame
import random
import sys
import websockets


# Pygame setup code
def ball_animation():
    global ball_speed_x, ball_speed_y, player_score, opponent_score, score_time
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1
    if ball.left <= 0:
        player_score += 1
        score_time = pygame.time.get_ticks()
    if ball.right >= screen_width:
        opponent_score += 1
        score_time = pygame.time.get_ticks()

    if ball.colliderect(player) or ball.colliderect(opponent):
        ball_speed_x *= -1


def player_animation(new_location):
    if new_location:
        player.y = new_location
    if player.top <= 0:
        player.top = 0
    if player.bottom >= screen_height:
        player.bottom = screen_height


def opponent_ai():
    if opponent.top < ball.y:
        opponent.top += opponent_speed
    if opponent.bottom > ball.y:
        opponent.bottom -= opponent_speed
    if opponent.top <= 0:
        opponent.top = 0
    if opponent.bottom >= screen_height:
        opponent.bottom = screen_height


def ball_start():
    global ball_speed_x, ball_speed_y, score_time

    current_time = pygame.time.get_ticks()
    ball.center = (screen_width / 2, screen_height / 2)

    if current_time - score_time < 700:
        number_three = game_font.render("3", False, light_grey)
        screen.blit(number_three, (screen_width / 2 - 10, screen_height / 2 + 20))
    if 700 < current_time - score_time < 1400:
        number_two = game_font.render("2", False, light_grey)
        screen.blit(number_two, (screen_width / 2 - 10, screen_height / 2 + 20))
    if 1400 < current_time - score_time < 2100:
        number_one = game_font.render("1", False, light_grey)
        screen.blit(number_one, (screen_width / 2 - 10, screen_height / 2 + 20))
    if current_time - score_time < 2100:
        ball_speed_x, ball_speed_y = 0, 0
    else:
        ball_speed_y = 7 * random.choice((1, -1))
        ball_speed_x = 7 * random.choice((1, -1))
        score_time = None


# General setup
pygame.init()
clock = pygame.time.Clock()

# Setting up the main window
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')

# Game Rectangles
ball = pygame.Rect(screen_width / 2 - 15, screen_height / 2 - 15, 30, 30)
player = pygame.Rect(screen_width - 20, screen_height / 2 - 70, 10, 140)
opponent = pygame.Rect(10, screen_height / 2 - 70, 10, 140)

# Colors
bg_color = pygame.Color('grey12')
light_grey = (200, 200, 200)

# Game Variables
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))
player_speed = 0
opponent_speed = 7

# Text Variables
player_score = 0
opponent_score = 0
game_font = pygame.font.Font("freesansbold.ttf", 32)

# Score Timer
score_time = True

# Position variable
position = None


async def receive_position(websocket):
    global position
    print("Starting to receive position data...")
    while True:
        try:
            message = await websocket.recv()
            print(f"Received message: {message}")
            message = message.decode('utf-8')
            if message.startswith("position="):
                position = float(message.split('=')[1])
                print(f"Updated position: {position}")
            else:
                print(f"Unknown message: {message}")
        except websockets.ConnectionClosed:
            print("Connection closed")
            break
        except Exception as e:
            print(f"Error: {e}")


async def game_loop():
    global position

    while True:
        # Handling input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Ball and player animation
        ball_animation()
        player_animation(screen_height - (position * screen_height / 100) if position is not None else None)
        opponent_ai()

        # Visuals
        screen.fill(bg_color)
        pygame.draw.rect(screen, light_grey, player)
        pygame.draw.rect(screen, light_grey, opponent)
        pygame.draw.ellipse(screen, light_grey, ball)
        pygame.draw.aaline(screen, light_grey, (screen_width / 2, 0), (screen_width / 2, screen_height))

        if score_time:
            ball_start()

        player_text = game_font.render(f"{player_score}", False, light_grey)
        screen.blit(player_text, (660, 470))

        opponent_text = game_font.render(f"{opponent_score}", False, light_grey)
        screen.blit(opponent_text, (600, 470))

        # Updating the window
        pygame.display.flip()
        clock.tick(60)

        await asyncio.sleep(0)  # Yield control to the event loop


async def main():
    uri = "ws://10.181.248.219:8080"  # Replace with your websocket URL
    async with websockets.connect(uri) as websocket:
        receive_task = asyncio.create_task(receive_position(websocket))
        game_task = asyncio.create_task(game_loop())
        await asyncio.gather(receive_task, game_task)


if __name__ == "__main__":
    asyncio.run(main())
