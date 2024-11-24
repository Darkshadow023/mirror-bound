import pygame
import sys
import random
from queue import Queue

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (350, 650)  # Actual window size
MAZE_SIZE = (300,500)    # Maze area size
CELL_SIZE = 20
PLAYER_SIZE = 16
PLAYER_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)

# Calculate grid dimensions
GRID_WIDTH = MAZE_SIZE[0] // CELL_SIZE
GRID_HEIGHT = MAZE_SIZE[1] // CELL_SIZE

# Calculate offset to center the maze
MAZE_OFFSET_X = (WINDOW_SIZE[0] - MAZE_SIZE[0]) // 2
MAZE_OFFSET_Y = (WINDOW_SIZE[1] - MAZE_SIZE[1]) // 2

# Load images
try:
    # Load and scale images to PLAYER_SIZE
    player_img = pygame.image.load('data/char_player.png')
    player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
    
    goal_img = pygame.image.load('data/portal.png')
    goal_img = pygame.transform.scale(goal_img, (30,30))
    
    # Load and scale background to maze size
    background_img = pygame.image.load('data/bg_main.png')
    background_img = pygame.transform.scale(background_img, WINDOW_SIZE)
except pygame.error as e:
    print(f"Couldn't load images from 'data' folder: {e}")
    print("Make sure you have the following files in your 'data' folder:")
    print("- player.png")
    print("- goal.png")
    print("- background.png")
    sys.exit(1)

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Mobile Maze Game")
clock = pygame.time.Clock()

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[True for _ in range(width)] for _ in range(height)]
        self.barriers = []
    
    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def generate(self):
        self.grid = [[True for _ in range(self.width)] for _ in range(self.height)]
        self._carve_paths(1, 1)
        
        self.barriers = []
        
        # Add outer walls (adjusted for offset)
        self.barriers.extend([  
            (MAZE_OFFSET_X, MAZE_OFFSET_Y, MAZE_OFFSET_X + MAZE_SIZE[0], MAZE_OFFSET_Y),  # Top
            (MAZE_OFFSET_X, MAZE_OFFSET_Y, MAZE_OFFSET_X, MAZE_OFFSET_Y + MAZE_SIZE[1]),  # Left
            (MAZE_OFFSET_X + MAZE_SIZE[0], MAZE_OFFSET_Y, MAZE_OFFSET_X + MAZE_SIZE[0], MAZE_OFFSET_Y + MAZE_SIZE[1]),  # Right
            (MAZE_OFFSET_X, MAZE_OFFSET_Y + MAZE_SIZE[1], MAZE_OFFSET_X + MAZE_SIZE[0], MAZE_OFFSET_Y + MAZE_SIZE[1])   # Bottom
        ])
        
        # Add internal walls (adjusted for offset)
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    # Add vertical line
                    self.barriers.append((  
                        x * CELL_SIZE + MAZE_OFFSET_X, 
                        y * CELL_SIZE + MAZE_OFFSET_Y, 
                        x * CELL_SIZE + MAZE_OFFSET_X, 
                        (y + 1) * CELL_SIZE + MAZE_OFFSET_Y
                    ))
                    # Add horizontal line
                    self.barriers.append((  
                        x * CELL_SIZE + MAZE_OFFSET_X, 
                        y * CELL_SIZE + MAZE_OFFSET_Y, 
                        (x + 1) * CELL_SIZE + MAZE_OFFSET_X, 
                        y * CELL_SIZE + MAZE_OFFSET_Y
                    ))
        
        return self.barriers
    
    def _carve_paths(self, x, y):
        self.grid[y][x] = False
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (self.is_valid(new_x, new_y) and self.grid[new_y][new_x] and 
                self.is_valid(x + dx//2, y + dy//2)):
                self.grid[y + dy//2][x + dx//2] = False
                self._carve_paths(new_x, new_y)

def line_circle_collision(line_start, line_end, circle_center, circle_radius):
    """More accurate collision detection between a line and a circle (player)"""
    # Vector from line start to end
    line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    # Vector from line start to circle center
    center_vec = (circle_center[0] - line_start[0], circle_center[1] - line_start[1])
    
    # Length of line squared
    line_length_sq = line_vec[0]**2 + line_vec[1]**2
    
    if line_length_sq == 0:
        # Line segment is actually a point
        dist = (center_vec[0]**2 + center_vec[1]**2)**0.5
        return dist <= circle_radius
    
    # Project center_vec onto line_vec to find closest point
    t = max(0, min(1, (center_vec[0]*line_vec[0] + center_vec[1]*line_vec[1]) / line_length_sq))
    
    # Find closest point on line to circle center
    closest_x = line_start[0] + t * line_vec[0]
    closest_y = line_start[1] + t * line_vec[1]
    
    # Check if distance from closest point to circle center is less than radius
    dx = circle_center[0] - closest_x
    dy = circle_center[1] - closest_y
    distance = (dx*dx + dy*dy)**0.5
    
    return distance <= circle_radius

def handle_movement(keys, player_rect, barriers):
    """Improved movement and collision handling"""
    move_x = 0
    move_y = 0
    
    if keys[pygame.K_LEFT]:
        move_x = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        move_x = PLAYER_SPEED
    if keys[pygame.K_UP]:
        move_y = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        move_y = PLAYER_SPEED
    
    # Try moving on X axis
    new_x = player_rect.x + move_x
    collision_x = False
    for barrier in barriers:
        if line_circle_collision(
            (barrier[0], barrier[1]), 
            (barrier[2], barrier[3]), 
            (new_x + PLAYER_SIZE//2, player_rect.y + PLAYER_SIZE//2),
            PLAYER_SIZE//2
        ):
            collision_x = True
            break
    
    # Try moving on Y axis
    new_y = player_rect.y + move_y
    collision_y = False
    for barrier in barriers:
        if line_circle_collision(
            (barrier[0], barrier[1]), 
            (barrier[2], barrier[3]), 
            (player_rect.x + PLAYER_SIZE//2, new_y + PLAYER_SIZE//2),
            PLAYER_SIZE//2
        ):
            collision_y = True
            break
    
    # Update position based on collisions
    if not collision_x:
        player_rect.x = new_x
    if not collision_y:
        player_rect.y = new_y
    
    # Keep player within maze bounds
    player_rect.x = max(MAZE_OFFSET_X, min(MAZE_OFFSET_X + MAZE_SIZE[0] - PLAYER_SIZE, player_rect.x))
    player_rect.y = max(MAZE_OFFSET_Y, min(MAZE_OFFSET_Y + MAZE_SIZE[1] - PLAYER_SIZE, player_rect.y))
    
    return player_rect

# Function to display win screen
def display_win_screen():
    import story2
    story2()
# Initialize game objects
maze_generator = MazeGenerator(GRID_WIDTH, GRID_HEIGHT)
player = pygame.Rect(MAZE_OFFSET_X + CELL_SIZE, MAZE_OFFSET_Y + CELL_SIZE, 
                    PLAYER_SIZE, PLAYER_SIZE)
goal = pygame.Rect(MAZE_OFFSET_X + MAZE_SIZE[0] - 2*CELL_SIZE, 
                  MAZE_OFFSET_Y + MAZE_SIZE[1] - 2*CELL_SIZE, 
                  PLAYER_SIZE, PLAYER_SIZE)

# Generate initial maze
barriers = maze_generator.generate()

# Game loop
running = True
won = False
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # Reset game with new maze
            barriers = maze_generator.generate()
            player.x = MAZE_OFFSET_X + CELL_SIZE
            player.y = MAZE_OFFSET_Y + CELL_SIZE
            won = False
    
    if not won:
        # Handle movement
        keys = pygame.key.get_pressed()
        player = handle_movement(keys, player, barriers)
        
        # Check for win condition
        if player.colliderect(goal):
            won = True
    
    # Drawing
    screen.fill(DARK_GRAY)
    
    if won:
        # Show the win screen
        display_win_screen()
    else:
        # Draw background
        screen.blit(background_img, (0,0))
        
        # Draw barriers
        for barrier in barriers:
            pygame.draw.line(screen, WHITE, (barrier[0], barrier[1]), 
                            (barrier[2], barrier[3]), 2)
        
        # Draw goal using image
        screen.blit(goal_img, goal)
        
        # Draw player using image
        screen.blit(player_img, player)
        
        # Draw text
        font = pygame.font.Font(None, 24)
        text = font.render('Press arrow keys to play!', True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_SIZE[0]/2, 50))
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
