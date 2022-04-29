import pygame
import pygame_gui
from pygame.locals import *

pygame.init()

width = 1000 # creates the windows width
height = 800    # creates the windows height 
window = pygame.display.set_mode((width, height))  # Creates the window 
background = pygame.Surface((1000, 800))    #Makes a background surface for GUI
background.fill(pygame.Color('black'))
bg_image = pygame.image.load("Background.png")          # Imports the image as for the background 
bg_image = pygame.transform.scale(bg_image,(1000,725))  # Scales the image to fit the window 

manager = pygame_gui.UIManager((1000, 800))
record_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 725), (300, 75)),   #Pygame Rect first pair coordinates second pair button size
                                            text='Record',  # Inside button text 
                                            manager=manager)

play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 725), (300, 75)),
                                            text='Play',
                                            manager=manager)


clock = pygame.time.Clock() #

runing = True           # While pygame is running 
while runing:
    window.blit(bg_image,(0,0)) # Creates the image variable and coordinate and places image into background window 
    for event in pygame.event.get():        
        if event.type == QUIT:
            runing = False
    pygame.display.update()


    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        manager.process_events(event)

    manager.update(time_delta)

    
    manager.draw_ui(window)

    pygame.display.update()
pygame.quit()