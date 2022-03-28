'''
Lays the groundwork of note creation and functions to implement them. Includes a Note class, and functions to play and stop when specified.

Also includes basic skeleton of the class for the GUI, MAIN, etc. We will have to change a lot around as the project progresses.
'''

from time import sleep
import pygame
import pygame_gui as pyg
from array import array

#constants
MIXER_FREQ = 44100
MIXER_SIZE = -16
MIXER_CHANS = 1
MIXER_BUFF = 1024

class Note(pygame.mixer.Sound):
    
    #volume ranges from 0.0 to 1.0
    def __init__(self, frequency, volume):
        self.frequency = frequency
        
        #initialize note from array of samples
        pygame.mixer.Sound.__init__(self, buffer = self.build_samples())
        self.set_volume(volume)
    
    def build_samples(self):
        
        #calculate the frequency and amplitude of the note's wave
        period = int(round(MIXER_FREQ / self.frequency))
        amplitude = 2 ** (abs(MIXER_SIZE) - 1) - 1
        
        #initialize the note's samples (using an array of signed 16-bit "shorts"
        samples = array("h", [0] * period)
        
        #generate the note's samples
        for t in range(period):
            if(t < period / 2):
                samples[t] = amplitude
            else:
                samples[t] = -amplitude
        
        return samples

class GUI(pyg.UIManager):
    pass



#waits until a note is pressed 
def wait_for_note_start(self):
    pass
    
#waits until a note is released
def wait_for_note_stop(self):
    pass


############
####MAIN####
############



# preset mixer initialization arguments: frequency (44.1K), size
# (16 bits signed), channels (mono), and buffer size (1KB)
# then, initialize the pygame library
pygame.mixer.pre_init(MIXER_FREQ, MIXER_SIZE, MIXER_CHANS, MIXER_BUFF)
pygame.init()

#creation of dictionary(ies)


#detects and initiates controller(s)
joysticks = []
for i in range(pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
for joystick in joysticks:
    joystick.init()

#creates pygame window
pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((800, 600))
background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    window_surface.blit(background, (0, 0))
    pygame.display.update()
