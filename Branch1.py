'''
Lays the groundwork of note creation and functions to implement them. Includes a Note class, and functions to play and stop when specified.

Also includes basic skeleton of the class for the GUI, MAIN, etc. We will have to change a lot around as the project progresses.
'''

from time import sleep
import pygame
import pygame_gui as pyg
from array import array
import math

#constants
MIXER_FREQ = 44100
MIXER_SIZE = -16
MIXER_CHANS = 1
MIXER_BUFF = 1024
DEFAULT_VOLUME = 1.0
PI = math.pi

class Note(pygame.mixer.Sound):
    
    #volume ranges from 0.0 to 1.0
    def __init__(self, frequency, volume):
        self.frequency = frequency
        
        #initialize note from array of samples
        pygame.mixer.Sound.__init__(self, buffer = self.build_samples())
        self.set_volume(volume)
    
    def build_samples(self):
        
        #calculate the frequency and amplitude of the note's wave
        period = int(round(MIXER_FREQ / self.frequency))                        # time of one wave = constant / frequency called from list
        amplitude = 2 ** (abs(MIXER_SIZE) - 1) - 1                              # amp = how loud the sound is
        
        #initialize the note's samples (using an array of signed 16-bit "shorts")
        samples = array("h", [0] * period)                                      # creates an array of 16 notes to play
        
        #generate the note's samples
        for t in range(period):                                                 # for time in the time of one wave
            if(t < period / 2):                                                 # if time is less than half
                samples[t] = amplitude  #sine wave is Asin(2pi/period(x))       # First 8 notes will pe positive
            else:
                samples[t] = -amplitude                                         # last 8 notes will be negative
        
        return samples

class GUI(pyg.UIManager):
    pass



#waits until a note is pressed 
def wait_for_note_start(self):
    pass
    
#waits until a note is released
def wait_for_note_stop(self):
    pass
    
def create_octaves(octaves, button_names, hat_names, hat_tuples, music_button_names):
    total_index = 0
    for octave in octaves.keys():                                                           # Iterate through octaves dictionary
        i = 0                                                                               # button value on controller
        for button in music_button_names:                                                   # for a button in the list music_button_names
            octaves[octave].update(button = (i, list_of_notes[total_index]))                # octaves - big dictionary - octave3 is updating button = 0 which is x button, very first item in freq_list
            octaves[octave][button] = octaves[octave].pop('button')                         # in the sub dictionary, makes the key = button,frequency of button and value = note name
            i += 1
            total_index += 1
        for index in range(len(hat_names)):
            octaves[octave].update(hat = (hat_tuples[index], list_of_notes[total_index]))
            octaves[octave][hat_names[index]] = octaves[octave].pop('hat')
            i += 1
            total_index += 1


############
####MAIN####
############

# preset mixer initialization arguments: frequency (44.1K), size
# (16 bits signed), channels (mono), and buffer size (1KB)
# then, initialize the pygame library
pygame.mixer.pre_init(MIXER_FREQ, MIXER_SIZE, MIXER_CHANS, MIXER_BUFF)              # Constants passed through pygame sound mixer
pygame.init()                                                                       # intiates the pygame
pygame.mixer.init()                                                                 # intiates the pygame sound mixer to play sound

#creation of list w/ every note
            #C      Db      D       Eb      E       F       Gb      G       Ab      A       Bb      B
freq_list = [130.8,	138.6,	146.8,	155.6,	164.8,	174.6,	185.0,	196.0,	207.7,	220.0,	233.1,	246.9, #octave3       # 48 items, 4 octaves, 
            261.6,	277.2,	293.7,	311.1,	329.6,	349.2,	370.0,	392.0,	415.3,	440.0,	466.2,	493.9, #octave4
            523.3,	554.4,	587.3,	622.3,	659.3,	698.5,	740.0,	784.0,	830.6,	880.0,	932.3,	987.8, #octave5
            1047,	1109,	1175,	1245,	1319,	1397,	1480,	1568,	1661,	1760,	1865,	1976]  #octave6

notes_names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]      # 12 items, 1 octave

list_of_notes = []                                      # When octave is changed, the list of notes that can be played is changed
for freq in freq_list:
    list_of_notes.append(Note(freq, DEFAULT_VOLUME))    # Calls from the frequency list and constant, to the Note class


#creation of master dictionary. Contains subdictionaries of each octave. each subdictionary has a key w/ a button name corresponding to a controller button
#and the value tied to the key will be the button_index that pygame reads and the note.
octave3 = {}
octave4 = {}
octave5 = {}
octave6 = {}

octaves = {                         # Dictionary of each octave dictionary
    "octave3" : octave3,
    "octave4" : octave4,
    "octave5" : octave5,
    "octave6" : octave6
}

button_names = ["x", "circle", "square", "triangle", "share", "options", "left_stick_click", "right_stick_click", "L1", "R1"]        
hat_names = ["up_arrow", "down_arrow", "left_arrow", "right_arrow"]
hat_tuples = [(0, 1), (0, -1), (-1, 0), (1, 0)]
music_button_names = ["x", "circle", "square", "triangle", "share", "options", "L1", "R1"]
 




#total_index = 0
#for octave in octaves.keys():                                                           # Iterate through octaves dictionary
#    i = 0                                                                               # button value on controller
#    for button in music_button_names:                                                   # for a button in the list music_button_names
#        octaves[octave].update(button = (i, list_of_notes[total_index]))                # octaves - big dictionary - octave3 is updating button = 0 which is x button, very first item in freq_list
#        octaves[octave][button] = octaves[octave].pop('button')                         # in the sub dictionary, makes the key = button,frequency of button and value = note name
#        i += 1
#        total_index += 1
#    for index in range(len(hat_names)):
#        octaves[octave].update(hat = (hat_tuples[index], list_of_notes[total_index]))
#        octaves[octave][hat_names[index]] = octaves[octave].pop('hat')
#        i += 1
#        total_index += 1


# Plays all notes tied to buttons (except the d pad) all in order (Used for testing)
'''
for octave in octaves:
    for buttonName in music_button_names:
        index, note = octaves[str(octave)][buttonName]
        note.play(100)
        pygame.time.wait(400)
'''

#detects and initiates controller(s)
joysticks = []                                              # list of joysticks/controllers
for i in range(pygame.joystick.get_count()):                # pygame automactically counts the number of controllers connected externally
    joysticks.append(pygame.joystick.Joystick(i))           # append the number of controllers to the list
for joystick in joysticks:                                  # For the amount of controllers in the joystick list
    joystick.init()                                         # Basically initiate the functions of the controller




currentOctave = 'octave3'
running = True
while running:
    
    for event in pygame.event.get():                            # Basically reads if you quit
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pass
        
        
        for buttonName in music_button_names:                   # for the button in the list of music_button_names
            index, note = octaves[currentOctave][buttonName]    # tuple = button index of sub dictionary 
            if joystick.get_button(index) == 1:                 # Reads if button is pushed and plays note
                note.play(-1)
            if joystick.get_button(index) == 0:                 # If button is released, stop playing note
                note.stop()
        for hatName in hat_names:
            hatTuple, note = octaves[currentOctave][hatName]
            if joystick.get_hat(0) == hatTuple:
                note.play(-1)
            if joystick.get_hat(0) != hatTuple:
                note.stop()

'''
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
'''
