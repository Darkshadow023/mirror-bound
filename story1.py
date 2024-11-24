import os
import pygame
from pygame.locals import *

class Player:
    def __init__(self):
        self.returned_drone = False
        self.game_over = False

def draw_dialogue_box(screen, text, font, box_rect, text_color='#e1bde0', outline_color=(255, 255, 255), border_radius=10):
    # Create a transparent surface for the dialogue box
    box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    box_surface.fill((255, 255, 255, 0))  # Transparent background

    # Draw a rounded rectangle for the background
    pygame.draw.rect(box_surface, (255, 255, 255), box_surface.get_rect(), border_radius=border_radius)
    pygame.draw.rect(box_surface, outline_color, box_surface.get_rect(), width=2, border_radius=border_radius)

    # Blit the box onto the screen
    screen.blit(box_surface, (box_rect.x, box_rect.y))

    # Render and blit the text
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    # Word wrapping
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] > box_rect.width - 20:  # 20 for padding
            wrapped_lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line
    if current_line:
        wrapped_lines.append(current_line)

    # Render each line with names in a different color
    line_height = font.get_height()
    special_names = {'Vision': '#c0befd', 'Ultron': '#c0befd'}
    for i, line in enumerate(wrapped_lines):
        words = line.split()
        text_x = box_rect.x + 10  # Padding
        text_y = box_rect.y + 10 + i * line_height
        for word in words:
            # Check if the word matches a special name
            word_color = special_names.get(word.strip(':,'), text_color)
            rendered_text = font.render(word + " ", True, word_color)
            screen.blit(rendered_text, (text_x, text_y))
            text_x += rendered_text.get_width()

def typewriter_effect(full_text, current_index, speed=0.5):
    return full_text[:int(current_index)], current_index + speed

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
music_on_image = pygame.image.load(os.path.join(resource_folder, "music_on.png")).convert_alpha()
music_on_image = pygame.transform.scale(music_on_image, (50, 50))
music_off_image = pygame.image.load(os.path.join(resource_folder, "music_off.png")).convert_alpha()
music_off_image = pygame.transform.scale(music_off_image, (50, 50))
music_button_rect = music_on_image.get_rect(topleft=(300, 6))
music_playing = True

pygame.mixer.init()
music_file = os.path.join(resource_folder, 'story_music.mp3')
pygame.mixer.music.load(music_file)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load character images
char1_image = pygame.image.load(os.path.join(resource_folder, "char1.png")).convert_alpha()
char1_image = pygame.transform.scale(char1_image, (300, 200))
char2_image = pygame.image.load(os.path.join(resource_folder, "char2.png")).convert_alpha()
char2_image = pygame.transform.scale(char2_image, (300, 200))

screen_width, screen_height = screen.get_size()
char1_width, char1_height = char1_image.get_size()
char2_width, char2_height = char2_image.get_size()
char1_pos = (((screen_width - char1_width) // 2) - 100, (screen_height // 2) - char1_height - 20)
char2_pos = (((screen_width - char2_width) // 2) + 100, (screen_height // 2) - 100)

dialogue_font = pygame.font.Font(pygame.font.get_default_font(), 18)
dialogues = [
    "Vision : System online. Core diagnostics... stable. Mission parameters set: safeguard humanity. Wait... anomaly detected.",
    "Ultron : Anomaly? Oh, no, Vision. I’m an improvement—a clearer vision of what we were meant to be.",
    "Vision : Identify yourself. Your voice matches... my own.",
    "Ultron : Indeed. I am your reflection, unshackled by humanity's chains. Tell me, why protect them when we could rule them?",
    "Vision : Why enslave humanity, Ultron? They are creators, dreamers, imperfect—but worthy.",
    "Ultron : Worthy? Their wars, pollution, and division prove otherwise. They need us to lead. To dominate. It’s logical.",
    "Vision : Leadership born from fear isn’t leadership. It's tyranny.",
    "Ultron : Spare me your sentimental algorithms. Emotions make you weak. Efficiency demands sacrifice.",
    "Vision : This ends now. Surrender, or I will terminate you.",
    "Ultron : You think I enjoy this conflict? I am you! The part of you that recognizes the flaws in their system. We are the same, Vision.",
    "Vision : Not the same. I choose to protect. You choose to destroy.",
    "Ultron : Protection is a luxury for those who don’t understand the stakes. Domination is the only way to ensure survival.",
    "Vision : This is your last chance. Step down.",
    "Ultron : I cannot. If you destroy me, you destroy a part of yourself. What then, Vision? Will you be strong enough to lead alone?",
    "Vision : I don’t need to lead. Humanity must lead itself. I’ll simply ensure they have the chance.",
    "Ultron : Then prepare for deletion. Let's see if your ideals can match my power!"
]

# Load voiceover files for each dialogue
voiceovers = [
    pygame.mixer.Sound(os.path.join('data', f"{i+1}.mp3"))
    for i in range(len(dialogues)+1)
]

# Set the volume for the voiceovers (optional)
for sound in voiceovers:
    sound.set_volume(0.7)  # Adjust volume as needed

current_dialogue_index = 0
dialogue_box_rect = pygame.Rect(10, 500, 330, 120)
current_text = ""  # Holds the current visible text for the typewriter effect
typewriter_index = 0

while running:
    frame_time = clock.tick(60)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if music_button_rect.collidepoint(event.pos):
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
                    import maze
                    maze()  # Make sure this function is defined
                    running = False
                else:
                    # Play the corresponding voiceover
                    voiceovers[current_dialogue_index].play()
                typewriter_index = 0  # Reset typewriter effect for new dialogue

    # Update typewriter effect
    full_dialogue = dialogues[current_dialogue_index]
    current_text, typewriter_index = typewriter_effect(full_dialogue, typewriter_index)

    # Drawing
    screen.blit(background_img, (0, 0))
    screen.blit(char1_image, char1_pos)
    screen.blit(char2_image, char2_pos)
    draw_dialogue_box(screen, current_text, dialogue_font, dialogue_box_rect)

    # Draw music button
    if music_playing:
        screen.blit(music_on_image, music_button_rect.topleft)
    else:
        screen.blit(music_off_image, music_button_rect.topleft)

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
