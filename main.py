import pygame
import sys
from random import randint
import json
import os
import time

pygame.init()  # Initialize pygame

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Screen dimensions
BACKGROUND_COLOR = (30, 30, 30)  # Background color
FONT_NAME = 'Helvetica'  # Font name
FONT_SIZE = 9  # Font size
LABEL_COLOR = (255, 255, 255)  # Label color

font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)  # Load the font

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('minigames by retr0')

def label(text, pos, color=(0,0,0)) -> None:
    """Render text label on the screen."""
    l = font.render(text, True, color)
    screen.blit(l, pos)

def load_sprites(path: str, size: tuple) -> tuple:
    """Load and scale sprites from a given directory."""
    images = [os.path.join(path, image) for image in os.listdir(path)]
    sprites = []
    for sprite in images:
        image = pygame.image.load(sprite)
        sprites.append(pygame.transform.scale(image, size))
    return sprites, images

class GridRect:
    def __init__(self, x_positon: int, y_position: int, width: int, height: int, color=(255,255,255)) -> None:
        """Initialize a grid rectangle."""
        self.grect = pygame.Rect(x_positon, y_position, width, height)
        self.color = color
        self.image = None
    
    def set_color(self, color) -> None:
        """Set the color of the rectangle."""
        self.color = color
    
    def set_image(self, image: str) -> None:
        """Set the image of the rectangle."""
        image = pygame.image.load(image)
        image = pygame.transform.scale(image, (self.grect.width, self.grect.height))
        self.image = image

class GameGrid:
    def __init__(self, blocksize: int) -> None:
        """Initialize the game grid with specified block size."""
        self.xblocks, self.yblocks = SCREEN_WIDTH // blocksize, SCREEN_HEIGHT // blocksize
        self.blocksize = blocksize
        self.gridrects = []
        for y in range(self.yblocks):
            for x in range(self.xblocks):
                self.gridrects.append(GridRect(x * self.blocksize if x != 0 else x,
                                              y * self.blocksize if y != 0 else y,
                                              self.blocksize,
                                              self.blocksize))
                
    def show(self, screen, border_width: int=0, border_radius=0) -> None:
        """Draw the grid on the screen."""
        for grect in self.gridrects:
            if grect.image:
                screen.blit(grect.image, grect.grect.topleft)
            else:
                pygame.draw.rect(screen, grect.color, grect.grect, border_width, border_radius)

class Editor:
    def __init__(self, sprites_path, gamegrid: GameGrid, size: tuple) -> None:
        """Initialize the editor with sprites and grid rectangles."""
        self.sprites = load_sprites(sprites_path, size)
        self.gamegrid = gamegrid
        self.gridrects = gamegrid.gridrects
        self.grect_index = 0
        self.sprite_index = 0
        self.change_image = False
        self.selectedgrect = self.gridrects[self.grect_index]
        self.gridrects[self.grect_index].image = self.sprites[0][self.sprite_index]
    
    def focus(self, index):
        """Focus on a specific grid rectangle, wrapping around if necessary."""
        self.grect_index = index % len(self.gridrects)  # Ensure index wraps around
        self.selectedgrect = self.gridrects[self.grect_index]
        self.gridrects[self.grect_index].image = self.sprites[0][self.sprite_index]
    
    def next_sprite(self, forward=True) -> None:
        """Switch to the next or previous sprite."""
        if forward:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites[0])
        else:
            self.sprite_index = (self.sprite_index - 1) % len(self.sprites[0])
        self.selectedgrect.image = self.sprites[0][self.sprite_index]
    
    def save_grid(self, filename):
        """Store gridrects in a file"""
        with open(f"{filename}.json", "w") as f:
            json.dump(self.gridrects, f)
    
    def load_grid(self, filename):
        """Load gridrects from a file"""
        with open(f"{filename}.json", "r") as f:
            self.gamegrid.gridrects = json.load(f)
            self.gridrects = json.load(f)

# Main loop
def main():
    clock = pygame.time.Clock()  # Set up the clock for controlling frame rate
    gamegrid = GameGrid(180 // 4)  # Initialize the game grid with specified block size
    editor = Editor(sprites_path="C:\\Users\\retr0\\Documents\\work\\game\\resources\\PNG\\Default-size\\",
                    gamegrid=gamegrid,
                    size=(gamegrid.blocksize, gamegrid.blocksize))
    try:
        editor.load_grid("map")
    except:
        pass
    running = True  # Main loop flag
    key_up_pressed = False
    key_down_pressed = False
    key_left_pressed = False
    key_right_pressed = False

    while running:
        for event in pygame.event.get():  # Event handling loop
            if event.type == pygame.QUIT:
                editor.save_grid("map")
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressx, pressy = pygame.mouse.get_pos()
                index = 0
                for grect in gamegrid.gridrects:
                    if grect.grect.collidepoint(pressx, pressy):
                        editor.focus(index)
                    index += 1
            if event.type == pygame.KEYDOWN:  # Key press events
                if event.key == pygame.K_UP:
                    key_up_pressed = True
                if event.key == pygame.K_DOWN:
                    key_down_pressed = True
                if event.key == pygame.K_LEFT:
                    key_left_pressed = True
                if event.key == pygame.K_RIGHT:
                    key_right_pressed = True
            if event.type == pygame.KEYUP:  # Key release events
                if event.key == pygame.K_UP:
                    key_up_pressed = False
                if event.key == pygame.K_DOWN:
                    key_down_pressed = False
                if event.key == pygame.K_LSHIFT:
                    key_lshift_pressed = False

        # Handle key presses
        if key_up_pressed:
            editor.next_sprite()
            key_up_pressed = False  # Reset to handle only one switch per press
        if key_left_pressed:
            editor.focus(editor.grect_index - 1)
            key_left_pressed = False  # Reset to handle only one switch per press
        if key_right_pressed:
            editor.focus(editor.grect_index + 1)
            key_right_pressed = False  # Reset to handle only one focus change per press
        if key_down_pressed:
            editor.next_sprite(forward=False)
            key_down_pressed = False  # Reset to handle only one focus change per press

        screen.fill(BACKGROUND_COLOR)  # Clear the screen with background color
        gamegrid.show(screen)  # Draw the game grid
        label(str(editor.sprites[1][editor.sprite_index].split('\\')[-1]) + " " + str(editor.grect_index), (0, 0), color=(255, 255, 255))  # Display current sprite name

        pygame.display.flip()  # Update the display
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pygame.quit()  # Quit pygame
    sys.exit()  # Exit the program

if __name__ == "__main__":
    main()  # Run the main loop
