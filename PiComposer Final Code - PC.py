'''
Completed Program. Fully functional on PC. Recording function does not work on Raspberry Pi.

PiComposer is an audio recording software that allows a user to create an audio track, playing notes using a DualShock 4 controller.
A recorded audio track is compiled into a .wav file and can be played back within the program. These files can also be taken out from the directory for external use if desired.
The program includes a fully interactive GUI, including buttons tied to the main functions of the program. The GUI also includes a title card in the bottom-right, a status bar in 
the top-left which prompts the user on what to do and a clock that tells the user how much time is left for recording.
'''

#imported modules
import time
import pygame
import pygame_gui as pyg

from array import array
import pyaudio
import wave

import os

#constants

#constants for Notes
MIXER_FREQ = 48024 
MIXER_SIZE = -16
MIXER_CHANS = 1
MIXER_BUFF = 2048
DEFAULT_VOLUME = 1.0

#constants for recording
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 2
RECORD_SECONDS = 10
DEV_INDEX = 2

#Creates notes based on inputted frequencies. Each note is created with square frequency waves.
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
        
        #initialize the note's samples (using an array of signed 16-bit "shorts")
        samples = array("h", [0] * period)
        
        #generate the note's samples
        for t in range(period):
            if(t < period / 2):
                samples[t] = amplitude 
            else:
                samples[t] = -amplitude
        
        return samples

#Creates a button. Differes from a TextString as the draw() function allows different colors of text to indicate when a button is selected.
class Button():
    def __init__(self, x, y, text, textFont = "Arial"):
        self.rawText = str(text)
        self.font = pygame.font.SysFont(textFont, 50)
        self.text = self.font.render(self.rawText, True, "red")
        self.rect = self.text.get_rect()
        self.rect.topleft = (x, y)
    
    #allows manipulation of rawText
    @property
    def rawText(self):
        return self._rawText
    @rawText.setter
    def rawText(self, newRT):
        self._rawText = newRT
    
    #draws the buttons onto the GUI
    def draw(self, selector):
    
        #differing colors to determine if button is selected and when it is pressed.
        if selector == 2:
            self.text = self.font.render(self.rawText, True, "green")
        elif selector == 1:
            self.text = self.font.render(self.rawText, True, "red")
        else:
            self.text = self.font.render(self.rawText, True, "white")
        screen.blit(self.text, (self.rect.x, self.rect.y))

#Creates a TextString in the top left of the window. Acts as a status bar for the user.
class TextString():
    def __init__(self, text):
        self.rawText = str(text)
        self.font = pygame.font.SysFont("Arial", 30)
        self.text = self.font.render(self.rawText, True, "blue")
        self.rect = self.text.get_rect()
        self.rect.topleft = (200, 125)
    
    @property
    def rawText(self):
        return self._rawText
    @rawText.setter
    def rawText(self, newRT):
        self._rawText = newRT
    
    #writes the string onto the GUI.
    def write(self):
        screen.blit(self.text, (self.rect.x, self.rect.y))

#Creates a black rectangle in the GUI. Used to cover up previous text so new text can appear clean. 
#Used as a refresher for the countdown clock.
class Rect():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self):
        pygame.draw.rect(screen, "black", self.rect)

#Organizes every note into a dictionary of dictionaries for quick and uniform access to each note.
#Each key-value pair contains two values: an index and a note. The index is used to tie a specific note to a button on the controller.
#Creates uniform controller mappings for each octave.
def create_octaves(octaves, button_names, hat_names, hat_tuples, music_button_names):
    #total_index determines what note is tied to each button on the control in the octave
    total_index = 0
    for octave in octaves.keys():
        #i variable determines what note goes to each button. Resets every octave to have uniformity between octaves.
        i = 0
        #D-Pad is considered a 'hat,' and therefore detection of a D-Pad press is determined by a specific tuple value.
        #Ties the first notes of an octave to the D-Pad buttons.
        for index in range(len(hat_names)):
            octaves[octave].update(hat = (hat_tuples[index], list_of_notes[total_index]))
            octaves[octave][hat_names[index]] = octaves[octave].pop('hat')
            total_index += 1
        #Ties the rest of the notes in the octave to the remaining buttons on the controller.
        for button in music_button_names:
            octaves[octave].update(button = (i, list_of_notes[total_index]))
            octaves[octave][button] = octaves[octave].pop('button')
            i += 1
            total_index += 1

#Changes the currentOctave to one higher.
def addOctave(currentOctave):
    octList = currentOctave.split("_")
    newNum = int(octList[1]) + 1
    newOctave = f"{octList[0]}_{newNum}"
    return newOctave

#Changes the currentOctave to one lower.
def subtractOctave(currentOctave):
    octList = currentOctave.split("_")
    newNum = int(octList[1]) - 1
    newOctave = f"{octList[0]}_{newNum}"
    return newOctave

#Initializes the program by clearing all previous audio files and initiating the audio stream for recording.
def initialize():
    #clears the directory of all previous audio output files
    print("Clearing Cache...")
    path = "/Program Files (x86)/Notepad++/"
    file_list = os.listdir(path)
    for file in file_list:
        fileNameList = file.split("_")
        if fileNameList[0] == "output":
            print(f"Deleted: {file}")
            os.remove(file)
    
    global p
    p = pyaudio.PyAudio()
    
    #creates the audio stream
    global stream
    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = MIXER_FREQ,
                    input = True,
                    input_device_index = DEV_INDEX,
                    frames_per_buffer = CHUNK)

#Updates the timer within the GUI
def updateTime(CLOCK, CLOCK_REFRESH, startTime):
    TIME_LEFT = Button(1450, 110, "Time Left:")
    
    endTime = time.time()
    CLOCK.rawText = str(round((RECORD_SECONDS - (endTime - startTime))))
    TIME_LEFT.draw(2)
    CLOCK.draw(2)
    pygame.display.update()
    CLOCK_REFRESH.draw()
    pygame.display.update()

#Allows for the recording of the audio played within the function and puts it into an array. 
#The array is compiled into a .wav file that can be accessed elsewhere in the program.    
def recording(output_filename):
    CLOCK = Button(1650, 110, RECORD_SECONDS)
    CLOCK_REFRESH = Rect(1650, 110, 100, 50)
    startTime = time.time()
    currentOctave = 'octave_3'
    frames = []
    while True:
        #reads all outputted audio from the speakers and records it in chunks of 1024 frames.
        for i in range(0, int(MIXER_FREQ / CHUNK * RECORD_SECONDS)):
            stream.start_stream()
            
            updateTime(CLOCK, CLOCK_REFRESH, startTime)
            
            data = stream.read(CHUNK, False)
            frames.append(data)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    pass
                
                updateTime(CLOCK, CLOCK_REFRESH, startTime)
                pygame.mixer.stop()
                for buttonName in music_button_names:
                    updateTime(CLOCK, CLOCK_REFRESH, startTime)
                    index, note = octaves[currentOctave][buttonName]
                    if joystick.get_button(index) == 1:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.find_channel().play(note)
                        note.play(-1)
                    if joystick.get_button(index) == 0:
                        note.stop()
                updateTime(CLOCK, CLOCK_REFRESH, startTime)
                for hatName in hat_names:
                    updateTime(CLOCK, CLOCK_REFRESH, startTime)
                    hatTuple, note = octaves[currentOctave][hatName]
                    if joystick.get_hat(0) == hatTuple:
                        note.play(-1)
                    if joystick.get_hat(0) != hatTuple:
                        note.stop()
                
                updateTime(CLOCK, CLOCK_REFRESH, startTime)
                if (joystick.get_axis(octave_buttons["L2"]) >= 0.98):
                    updateTime(CLOCK, CLOCK_REFRESH, startTime)
                    if currentOctave != "octave_3":
                        currentOctave = subtractOctave(currentOctave)
                        pygame.time.wait(100)
                        print(currentOctave)
                if (joystick.get_axis(octave_buttons["R2"]) >= 0.98):
                    updateTime(CLOCK, CLOCK_REFRESH, startTime)
                    if currentOctave != "octave_6":
                        currentOctave = addOctave(currentOctave)
                        pygame.time.wait(100)
                        print(currentOctave) 
                updateTime(CLOCK, CLOCK_REFRESH, startTime)
                
        print("* done recording")
        stream.stop_stream()
        break
    pygame.mixer.stop()
    #detects if the name for a new file already exists. If so, creates a new file name.
    if os.path.exists(output_filename + ".wav"):
        fileNameList = output_filename.split("_")
        newFileNumber = str(int(fileNameList[1]) + 1)
        output_filename = fileNameList[0] + "_" + newFileNumber
    #creates new .wav file for most recent track recorded
    wf = wave.open(output_filename + ".wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(MIXER_FREQ)
    wf.writeframes(b''.join(frames))
    wf.close()
    return output_filename

#Allows the user to use the program without recording any audio.
#Can be used in the future as a 'practice' function.
def freeplay():
    CLOCK = Button(1650, 110, RECORD_SECONDS)
    CLOCK_REFRESH = Rect(1650, 110, 100, 50)
    currentOctave = 'octave_3'
    frames = []
    startTime = time.time()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
            pygame.mixer.stop()
            for buttonName in music_button_names:
                index, note = octaves[currentOctave][buttonName]
                if joystick.get_button(index) == 1:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.find_channel().play(note)
                    note.play(-1)
                if joystick.get_button(index) == 0:
                    note.stop()
            for hatName in hat_names:
                hatTuple, note = octaves[currentOctave][hatName]
                if joystick.get_hat(0) == hatTuple:
                    note.play(-1)
                if joystick.get_hat(0) != hatTuple:
                    note.stop()
                
            if (joystick.get_axis(octave_buttons["L2"]) >= 0.98):
                if currentOctave != "octave_3":
                    currentOctave = subtractOctave(currentOctave)
                    pygame.time.wait(100)
                    print(currentOctave)
            if (joystick.get_axis(octave_buttons["R2"]) >= 0.98):
                if currentOctave != "octave_6":
                    currentOctave = addOctave(currentOctave)
                    pygame.time.wait(100)
                    print(currentOctave)
        updateTime(CLOCK, CLOCK_REFRESH, startTime)
        endTime = time.time()
        
        if (endTime - startTime) >= RECORD_SECONDS:
            print("Freeplay Ended.")
            break
    pygame.mixer.stop()

#Plays back the latest audio file that was recorded. If nothing has been recorded prior to the implementation of this function, it prints a notice to the user in the GUI. 
def playbackAudio(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.set_volume(1)
        print("Playing Audio:")
        pygame.mixer.music.play()
        
        CLOCK = Button(1650, 110, RECORD_SECONDS)
        CLOCK_REFRESH = Rect(1650, 110, 100, 50)
        startTime = time.time()
        endTime = time.time()
        while RECORD_SECONDS > (endTime - startTime):
            PLAYBACK.write()
            updateTime(CLOCK, CLOCK_REFRESH, startTime)
            endTime = time.time()
    except:
        startTime = time.time()
        endTime = time.time()
        while (endTime - startTime) < 3.5:
            NO_PLAYBACK.write()
            pygame.display.update()
            endTime = time.time()

############
####MAIN####
############

# preset mixer initialization arguments: frequency (44.1K), size
# (16 bits signed), channels (mono), and buffer size (1KB)
# then, initialize the pygame library
pygame.mixer.pre_init(MIXER_FREQ, MIXER_SIZE, MIXER_CHANS, MIXER_BUFF)
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(10)


#creation of list w/ every note
            #C      Db      D       Eb      E       F       Gb      G       Ab      A       Bb      B
freq_list = [130.8,	138.6,	146.8,	155.6,	164.8,	174.6,	185.0,	196.0,	207.7,	220.0,	233.1,	246.9, #octave3
            261.6,	277.2,	293.7,	311.1,	329.6,	349.2,	370.0,	392.0,	415.3,	440.0,	466.2,	493.9, #octave4
            523.3,	554.4,	587.3,	622.3,	659.3,	698.5,	740.0,	784.0,	830.6,	880.0,	932.3,	987.8, #octave5
            1047,	1109,	1175,	1245,	1319,	1397,	1480,	1568,	1661,	1760,	1865,	1976]  #octave6

notes_names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

list_of_notes = []
for freq in freq_list:
    list_of_notes.append(Note(freq, DEFAULT_VOLUME))


#creation of master dictionary. Contains subdictionaries of each octave. each subdictionary has a key w/ a button name corresponding to a controller button
#and the value tied to the key will be the button_index that pygame reads and the note.
octave3 = {}
octave4 = {}
octave5 = {}
octave6 = {}

octaves = {
    "octave_3" : octave3,
    "octave_4" : octave4,
    "octave_5" : octave5,
    "octave_6" : octave6
}

#parallel lists and dictionary for the creation of octaves
button_names = ["x", "circle", "square", "triangle", "share", "options", "left_stick_click", "right_stick_click", "L1", "R1"]              
hat_names = [ "down_arrow", "right_arrow", "left_arrow", "up_arrow"]
hat_tuples = [(0, -1), (1, 0), (-1, 0), (0, 1)]
music_button_names = ["x", "circle", "square", "triangle", "share", "options", "L1", "R1"]
octave_buttons = {"L2" : 4, "R2" : 5}

create_octaves(octaves, button_names, hat_names, hat_tuples, music_button_names)



#detects and initiates controller(s)
joysticks = []
for i in range(pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
for joystick in joysticks:
    joystick.init()

#GUI window
window_size = (1920, 1080)

#name of .wav file
global output_filename
output_filename = "output_0"


initialize()

#creates the initial pygame window
clock = pygame.time.Clock()
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("PiComposer")

TITLE_CARD = Button(1400, 900, "PiComposer", "Algerian")
record_button = Button(250, 900, "Record")
freeplay_button = Button(900, 900, "Freeplay")
playBack_button = Button(500, 900, "Playback Audio")
selectorRecord = 0
selectorPlay = 0
selectorplayBack = 0

bottom_border = Rect(0, 900, 1920, 180)
top_border = Rect(0, 0, 1920, 175)

#all text strings used as a status to tell the user what to do.
NOW_RECORDING = TextString("You are now recording. Use the controller to play notes!")
NOW_FREEPLAY = TextString("You are now using freeplay. Use the controller to play notes. Nothing will be recorded.")
PLAYBACK = TextString("Now playing the last recorded audio track.")
NO_PLAYBACK = TextString("There is no audio track. Try recording using the 'Record' button.")


#creates the background image for the GUI
bg_img = pygame.image.load('orchestra.jpg')
bg_img = pygame.transform.scale(bg_img, window_size)

running = True
while running:
    
    screen.blit(bg_img, (0, 0))
    
    bottom_border.draw()
    top_border.draw()
    TITLE_CARD.draw(0)
    record_button.draw(selectorRecord)
    freeplay_button.draw(selectorPlay)
    playBack_button.draw(selectorplayBack)
    
    
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        #logic on how to color each button to highlight the current button selected in the GUI
        #number 0 = white button label, number 1 = red button label
        if joystick.get_hat(0) == (-1, 0):
            selectorRecord = 1
            selectorPlay = 0
            selectorplayBack = 0
        
        if joystick.get_hat(0) == (1, 0):
            selectorRecord = 0
            selectorPlay = 1
            selectorplayBack = 0
        
        if joystick.get_hat(0) == (0, -1):
            selectorRecord = 0
            selectorPlay = 0
            selectorplayBack = 1
        
        if joystick.get_hat(0) == (0, 1):
            selectorRecord = 1
            selectorPlay = 0
            selectorplayBack = 0
        
        #executes the corresponding function to what button is selected
        #highlights the button green
        if joystick.get_button(0) == 1:
            #begins the recording function
            if selectorRecord == 1:
                selectorRecord = 2
                record_button.draw(selectorRecord)
                NOW_RECORDING.write()
                pygame.display.update()
                output_filename = recording(output_filename)
                selectorRecord = 1
            #begins freeplay
            elif selectorPlay == 1:
                selectorPlay = 2
                freeplay_button.draw(selectorPlay)
                NOW_FREEPLAY.write()
                pygame.display.update()
                freeplay()
                selectorPlay = 1
            #loads and plays the audio track in the pygame mixer
            elif selectorplayBack == 1:
                selectorplayBack = 2
                playBack_button.draw(selectorplayBack)
                pygame.display.update()
                file = output_filename + ".wav"
                playbackAudio(file)
                selectorplayBack = 1
    
    pygame.display.update()

pygame.quit()
