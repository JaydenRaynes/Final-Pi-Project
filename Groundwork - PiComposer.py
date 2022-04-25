'''
Program can now control when someone wants to enter notes by the PS button on the controller. Pressing it once begins recording.
Recording has limited time based on RECORD_SECONDS constant - 1. Can record multiple times and play the most recent audio file back.
Current Version works ONLY on PC/Windows 10.
'''

import time
import pygame
import pygame_gui as pyg

from array import array
import math

import pyaudio
import wave

import os
import shutil

import RPi.GPIO as GPIO

#constants
MIXER_FREQ = 48024 #changed constant so notes will be in tune
MIXER_SIZE = -16
MIXER_CHANS = 1
MIXER_BUFF = 1024
DEFAULT_VOLUME = 1.0

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RECORD_SECONDS = 7

DEV_INDEX = 2

#note class. Creates notes
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

class GUI(pyg.UIManager):
    pass
    
class Violin:
    G3 = Note(196, 1)
    D4 = Note(293.7, 1)
    A4 = Note(440, 1)
    E5 = Note(659.3, 1)

#creates dictionary of dictionaries of Notes.
def create_octaves(octaves, button_names, hat_names, hat_tuples, music_button_names):
    #total_index determines what note is tied to each button on the control in the octave
    total_index = 0
    for octave in octaves.keys():
        #i determines what button a pitch is tied to. Resets every octave
        i = 0
        #D-Pad is now the first to iterate, therefore has the lowest notes
        for index in range(len(hat_names)):
            octaves[octave].update(hat = (hat_tuples[index], list_of_notes[total_index]))
            octaves[octave][hat_names[index]] = octaves[octave].pop('hat')
            total_index += 1
        for button in music_button_names:
            octaves[octave].update(button = (i, list_of_notes[total_index]))
            octaves[octave][button] = octaves[octave].pop('button')
            i += 1
            total_index += 1

#changes the currentOctave to one higher.
def addOctave(currentOctave):
    octList = currentOctave.split("_")
    newNum = int(octList[1]) + 1
    newOctave = f"{octList[0]}_{newNum}"
    return newOctave

#changes the currentOctave to one lower.
def subtractOctave(currentOctave):
    octList = currentOctave.split("_")
    newNum = int(octList[1]) - 1
    newOctave = f"{octList[0]}_{newNum}"
    return newOctave

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
pygame.mixer.init()

# use the Broadcom pin mode
GPIO.setmode(GPIO.BCM)

# setup the pins for LEDs
octave_3_output = 20
octave_4_output = 16
octave_5_output = 12
octave_6_output = 26

# setup the output for octaves
GPIO.setup(octave_3_output, GPIO.OUT)
GPIO.setup(octave_4_output, GPIO.OUT)
GPIO.setup(octave_5_output, GPIO.OUT)
GPIO.setup(octave_6_output, GPIO.OUT)

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


currentOctave = 'octave_3'
recordButton = 10
recording = False
seconds = 3

'''
print(sd.query_devices())
[4] Speakers (Realtek(R) Audio), MME
[10] Speakers (Realtek(R) Audio), Windows DirectSound
[13] Speakers (Realtek(R) Audio), Windows WASAPI
[22] Speakers 1 (Realtek HD Audio output with SST), Windows WDM-KS
[23] Speakers 2 (Realtek HD Audio output with SST), Windows WDM-KS
'''
#clears the directory of all previous audio output files
print("Clearing Cache...")
path = "/Program Files (x86)/Notepad++/"
file_list = os.listdir(path)
for file in file_list:
    fileNameList = file.split("_")
    if fileNameList[0] == "output":
        print(f"Deleted: {file}")
        os.remove(file)

p = pyaudio.PyAudio()
#retrieves information on all current devices connected to PC.
#for i in range(p.get_device_count()):
#    print(p.get_device_info_by_index(i))

#creates the audio stream
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = MIXER_FREQ,
                input = True,
                input_device_index = DEV_INDEX,
                frames_per_buffer = CHUNK)


#name of .wav file
output_filename = "output_0"

running = True
print("Ready to go!")
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pass
        
        #begins the recording process with the press of the "PS" button on controller. Records for seconds specified by RECORD_SECONDS constant.
        #Takes the output of the speakers by chunk of frames and creates an array. Array is transferred to a .wav file.
        if joystick.get_button(recordButton) == 1:
            print("Recording started")
            frames = []
            while True:
                for i in range(0, int(MIXER_FREQ / CHUNK * RECORD_SECONDS)):
                    stream.start_stream()
                    data = stream.read(CHUNK, False)
                    frames.append(data)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            pass
                        pygame.mixer.stop()
                        for buttonName in music_button_names:
                            index, note = octaves[currentOctave][buttonName]
                            if joystick.get_button(index) == 1:
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
                if (currentOctave == "octave_3"):
                    GPIO.output(octave_3_output, True)
                    GPIO.output(octave_4_output, False)
                    GPIO.output(octave_5_output, False)
                    GPIO.output(octave_6_output, False)
                if (currentOctave == "octave_4"):
                    GPIO.output(octave_4_output, True)
                    GPIO.output(octave_5_output, False)
                    GPIO.output(octave_6_output, False)
                    GPIO.output(octave_3_output, False)                    
                if (currentOctave == "octave_5"):
                    GPIO.output(octave_5_output, True)
                    GPIO.output(octave_6_output, False)
                    GPIO.output(octave_3_output, False)
                    GPIO.output(octave_4_output, False)
                if (currentOctave == "octave_6"):
                    GPIO.output(octave_6_output, True)
                    GPIO.output(octave_3_output, False)
                    GPIO.output(octave_4_output, False)
                    GPIO.output(octave_5_output, False)
                print("* done recording")
                stream.stop_stream()
                break
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
        
        #loads the audio track into the pygame mixer
        #plays the current audio output file by push of the "X" button on controller.
        if joystick.get_button(0) == 1:
            try:
                pygame.mixer.music.load(output_filename + ".wav")
                pygame.mixer.music.set_volume(1)
                print("Playing Audio:")
                pygame.mixer.music.play()
            except:
                print("There is no recording present. Try recording using the 'PS' button")
                
