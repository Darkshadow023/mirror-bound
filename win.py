import os
import pygame
from pygame.locals import *

class Player:
    def __init__(self):
        self.returned_drone = False
        self.game_over = False

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centers the window
pygame.display.set_caption('MirrorBound')
screen = pygame.display.set_mode((350, 650))

# Initialize game variables
running = True
clock = pygame.time.Clock()
background_img = pygame.image.load('data/loading_screen.png')
screen.blit(background_img, (0, 0))

# Define the folder for resources
resource_folder = "data"

# Load custom button images
try:
    music_on_image = pygame.image.load(os.path.join(resource_folder, "music_on.png")).convert_alpha()
    music_on_image = pygame.transform.scale(music_on_image, (50, 50))
    music_off_image = pygame.image.load(os.path.join(resource_folder, "music_off.png")).convert_alpha()
    music_off_image = pygame.transform.scale(music_off_image, (50, 50))
    music_button_rect = music_on_image.get_rect(topleft=(300, 6))  # Position in the top-right corner
except pygame.error as e:
    print(f"Error loading button images: {e}")
    running = False  # Exit the game if images fail to load

music_playing = True

# Load and play background music
pygame.mixer.init()
music_file = os.path.join(resource_folder, "background_music.mp3")
try:
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
except pygame.error as e:
    print(f"Error loading music: {e}")

# Add variable to check if the player won
player_won = False

while running:
    frame_time = clock.tick(60)  # Limit the frame rate to 60 FPS

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            if music_button_rect.collidepoint(event.pos):  # Check if click is within music button bounds
                if music_playing:
                    pygame.mixer.music.pause()
                    music_playing = False
                else:
                    pygame.mixer.music.unpause()
                    music_playing = True

            # Example condition for winning the game (you can adjust based on your game logic)
            # For now, it's triggered by clicking anywhere on the screen.
            if not player_won:
                player_won = True  # Set the player_won flag to True to display the message

    # Drawing
    screen.blit(background_img, (0, 0))
    if music_playing:
        screen.blit(music_on_image, music_button_rect.topleft)
    else:
        screen.blit(music_off_image, music_button_rect.topleft)

    # Display "You Win" message if player won
    if player_won:
        font = pygame.font.Font(None, 74)
        win_text = font.render("You Win!", True, (255, 255, 255))  # White text
        text_rect = win_text.get_rect(center=(175, 325))  # Position it at the center
        screen.blit(win_text, text_rect)

    pygame.display.flip()  # Update the display

# Stop music and quit Pygame
pygame.mixer.music.stop()
pygame.quit()
