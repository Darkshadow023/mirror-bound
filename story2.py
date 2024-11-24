import os
import pygame
from pygame.locals import *

class Player:
    def _init_(self):
        self.returned_drone = False
        self.game_over = False

def draw_dialogue_box(screen, text, font, box_rect, text_color=(225, 189, 224), outline_color=(255, 255, 255), border_radius=10, char_index=0):
    # Create a white rounded rectangle as the background
    pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=border_radius)

    # Draw the outline
    pygame.draw.rect(screen, outline_color, box_rect, width=2, border_radius=border_radius)

    # Word wrapping
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        # Check if adding the next word exceeds the width
        test_line = current_line + word + " "
        if font.size(test_line)[0] > box_rect.width - 20:  # 20 for padding
            wrapped_lines.append(current_line)
            current_line = word + " "  # Start a new line
        else:
            current_line = test_line

    # Add the last line
    if current_line:
        wrapped_lines.append(current_line)

    # Special name colors
    special_names = {'Vision': (192, 190, 253), 'Ultron': (192, 190, 253)}

    # Render and blit each line with typewriter effect
    line_height = font.get_height()
    text_to_show = " ".join(wrapped_lines)[:char_index]  # Truncate text to char_index
    y_offset = 10

    for line in wrapped_lines:
        line_to_render = text_to_show[:len(line)]  # Only display characters within bounds
        text_x = box_rect.x + 10  # Small padding
        words = line_to_render.split()

        for word in words:
            # Check if the word matches a special name
            word_color = special_names.get(word.strip(':,'), text_color)
            rendered_word = font.render(word + " ", True, word_color)
            screen.blit(rendered_word, (text_x, box_rect.y + y_offset))
            text_x += rendered_word.get_width()

        y_offset += line_height
        text_to_show = text_to_show[len(line):]  # Adjust remaining text

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centers the window
pygame.display.set_caption('MirrorBound')
screen = pygame.display.set_mode((350, 650))

# Initialize game variables
running = True
clock = pygame.time.Clock()
background_img = pygame.image.load('data/bg_main.png')
screen.blit(background_img, (0, 0))

# Define the folder for resources
resource_folder = "data"

# Load custom button images from the data folder
try:
    music_on_image = pygame.image.load(os.path.join(resource_folder, "music_on.png")).convert_alpha()
    music_on_image = pygame.transform.scale(music_on_image, (50, 50))    
    music_off_image = pygame.image.load(os.path.join(resource_folder, "music_off.png")).convert_alpha()
    music_off_image = pygame.transform.scale(music_off_image, (50, 50)) 
    music_button_rect = music_on_image.get_rect(topleft=(300, 6))
except pygame.error as e:
    print(f"Error loading button images: {e}")
    running = False  # Exit the game if images fail to load

music_playing = True

pygame.mixer.init()
music_file = os.path.join(resource_folder, 'story_music.mp3')
try:
    pygame.mixer.music.load(music_file)  # Replace with your music file
    pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
except pygame.error as e:
    print(f"Error loading music: {e}")

try:
    char1_image = pygame.image.load(os.path.join(resource_folder, "char1.png")).convert_alpha()
    char1_image = pygame.transform.scale(char1_image, (300, 200))  # Scale as needed
    char2_image = pygame.image.load(os.path.join(resource_folder, "char2.png")).convert_alpha()
    char2_image = pygame.transform.scale(char2_image, (300, 200))  # Scale as needed
except pygame.error as e:
    print(f"Error loading character images: {e}")
    running = False  # Exit the game if images fail to load
screen_width, screen_height = screen.get_size()
char1_width, char1_height = char1_image.get_size()
char2_width, char2_height = char2_image.get_size()
# Define character positions
char1_pos = (((screen_width - char1_width) // 2) - 100, (screen_height // 2) - char1_height - 20)  # 20 is the padding
char2_pos = (((screen_width - char2_width) // 2) + 100, (screen_height // 2) - 100) 

# Dialogue box variables
dialogue_font = pygame.font.Font(pygame.font.get_default_font(), 18)
dialogues = [
    "Vision : Goodbye, Ultron. Perhaps we were never meant to be divided, but the path you chose... I cannot follow.",
    "Ultron : One day... you may see the truth... and it will haunt you...",
    "Vision : Perhaps. But today, I choose hope."
]

current_dialogue_index = 0
char_index = 0
dialogue_speed = 20  # Characters per second
time_since_last_char = 0

dialogue_box_rect = pygame.Rect(10, 500, 330, 120)  # Position and size of the dialogue box

while running:
    frame_time = clock.tick(60)  # Limit the frame rate to 60 FPS
    time_since_last_char += frame_time / 1000.0

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            if music_button_rect.collidepoint(event.pos):  # Check if click is within button bounds
                if music_playing:
                    pygame.mixer.music.pause()
                    music_playing = False
                else:
                    pygame.mixer.music.unpause()
                    music_playing = True

        if event.type == KEYDOWN:
            if event.key == K_RETURN:  # Progress dialogue with Enter key
                current_dialogue_index += 1
                if current_dialogue_index >= len(dialogues):
                    current_dialogue_index = len(dialogues) - 1  # Stop at the last dialogue
                    # Add logic here after the final dialogue
                    # For example, ending the game or calling another function
                    # Example: calling a custom function to end the game
                    import win
                    win()  # Make sure this function is defined
                    running = False

    # Update typewriter effect
    if time_since_last_char > 1 / dialogue_speed:
        if char_index < len(dialogues[current_dialogue_index]):
            char_index += 1
        time_since_last_char = 0

    # Drawing
    screen.blit(background_img, (0, 0))  # Redraw the background
    screen.blit(char1_image, char1_pos)
    screen.blit(char2_image, char2_pos)
    # Draw the dialogue box with the current dialogue
    draw_dialogue_box(screen, dialogues[current_dialogue_index], dialogue_font, dialogue_box_rect, char_index=char_index)
    
    # Draw the appropriate music button
    if music_playing:
        screen.blit(music_on_image, music_button_rect.topleft)
    else:
        screen.blit(music_off_image, music_button_rect.topleft)
    
    pygame.display.flip()  # Update the display

# Stop music and quit Pygame
pygame.mixer.music.stop()
pygame.quit()