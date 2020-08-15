"""
	Pyano
	A midi based piano and keyboard learning game 
	29.06.2020. N3cr0
"""
import pygame
import time
import numpy
import midi
import sys
import itertools
import os
from tkinter import filedialog
from tkinter import *
from rtmidi.midiutil import open_midiinput
from mingus.midi import fluidsynth
from operator import itemgetter

#Midi Functions:

def initMidiIn():
	try:
		midiin, port_name = open_midiinput(1)
		return midiin, port_name
	except:
		print("Midi Error: Midi input failed to initiate")

def initMidiOut():
	try:
		fluidsynth.init('Piano.sf2',"alsa")
	except:
		print("Midi Error: Midi output failed to initiate")

def playMidiInput(midiInput):
	global keys
	if midiInput != '':
		key = int(midiInput[0][1])
		keys[key] = not keys[key]
		fluidsynth.play_Note(key, 0, keys[key]*100)	

def getMidiInput(midiDevice):
	Input = midiDevice.get_message()
	if Input:
		return Input
	return ''

def loadSongMidiPattern(midiFile):
	try:
		pattern = midi.read_midifile(midiFile)
		pattern.make_ticks_abs()
		return pattern
	except:
		print("Failed to load midi pattern")

def convertPatternToScore(pattern):
#TODO	#This function repeats itself see what we can do to fix it
	pattern = numpy.concatenate(pattern)
	notes = []
	for e in pattern:
		if "Note" in str(e):
			eventType = 0
			if "NoteOn" in str(e):
				eventType = 1
				if e.get_velocity == 0:
					eventType = 0;
			#Note format
			notes.append([e.tick, e.get_pitch(), eventType, e.channel])
	score=[]
	openNotes=[]
	for note in notes:
		if note[2] == 1:
			openNotes.append([note[0], [note[1], note[3]]])
		else:
			for n in openNotes:
				if n[1][0] == note[1]:
					score.append([n[0], note[1], note[0]-n[0], note[3]])
					openNotes.remove(n)
	return sorted(score, key=itemgetter(0))

def getTickTime(MPQN, patternRes):
	return MPQN/patternRes;

def getPatternMPQN(midiPattern):
	pattern = numpy.concatenate(midiPattern)
	MPQN=60000
	for e in pattern:
		if "SetTempo" in str(e):
			MPQN = int(e.get_mpqn())
	return MPQN
def getPatternRes(midiPattern):
	return int(midiPattern.resolution)

#Display functions:

def midiFileChooser():
	r = Tk()
	r.filename = filedialog.askopenfilename(initialdir = "",title ="Select a MIDI file" , filetypes = (("MIDI", "*.mid"),("All files", "*")))
	Song=os.path.relpath(r.filename)
	r.destroy()
	return Song

#If the keys dont end up fitting then edit this to 
def getKeyWidth(windowWidth):
	global NUMBER_OF_KEYS
	return int(windowWidth / (NUMBER_OF_KEYS / 12*7))

def getKeyHeight(windowHeight, petternRes):
	return windowHeight/ patternRes / 10
def loadKeyImage(imageLink, keyWidth, keyHeight):
	image = pygame.image.load(imageLink)
	image = pygame.transform.scale(image,(keyWidth, keyHeight))
	return image

def createWindow(dimentions, name, icon):
	icon = pygame.image.load("icon.png")
	window = pygame.display.set_mode(dimentions)
	pygame.display.set_caption('Pyano')
	pygame.display.set_icon(icon);
	return window

#Game Graphics:

def drawBackground():
	global NUMBER_OF_KEYS, keyWIdth, windowHegith;
	Window.fill((80,80,80))
	#Draw Lines:
	for i in range(0, int(NUMBER_OF_KEYS/7)):
		pygame.draw.rect(Window, (250,250,250), ( i*keyWidth*7,0, 1,windowHeight))
		pygame.draw.rect(Window, (150,150,150), ( i*keyWidth*7+(keyWidth*3),0, 1,windowHeight))

#DrawKeys:
def drawKeys(Keys):
	NUBBER_OF_KEYS = len(Keys);
	#White Keys:
	c=0
	for i in range(0,NUMBER_OF_KEYS):
		if( i%12 not in [1,3,6,8,10] ):
			if not keys[i]:
				Window.blit(whiteKey, (c,windowHeight-80));
			else:
				Window.blit(whiteKeyP, (c,windowHeight-80));
			c=c+keyWidth
	#Black Keys:
	c=keyWidth/2
	for i in range(0,NUMBER_OF_KEYS):
		if( i%12 in [1,3,6,8,10] ):
			if not keys[i]:
				Window.blit(blackKey, (c,windowHeight-80));
			else:
				Window.blit(blackKeyP, (c,windowHeight-80));
			c=c+keyWidth
		if (i%12 in [3, 10]):
			c=c+keyWidth
def drawNotes(Score):
	for e in Score:
		t = e[1]%12
		octave=int(e[1]/12)
		x=octave*7*keyWidth
		#White notei:
		if t not in [1,3,6,8,10]:
			if t in [0,2,4]:
				x=x+t/2*keyWidth
			if t in [5]:
				x=x+3*keyWidth
			if t in [7,9,11]:
				x=x+(t+1)/2*keyWidth
			#border
			pygame.draw.rect(Window, (0,0,0), ( x,graphicsOffset-(e[0]*tickHeight), keyWidth,e[2]*tickHeight));
			#fillColor
			pygame.draw.rect(Window, channelColor[e[3]][0], ( x+2,graphicsOffset-(e[0]*tickHeight)+2, keyWidth-4,e[2]*tickHeight-4));
		#black keys
		else:
			if t in [1,3]:
				x=x+int(t/2)*keyWidth+(keyWidth/2)
			if t in [6,8,10]:
				x=x+(t/2)*keyWidth+keyWidth/2
			#border
			pygame.draw.rect(Window, (0,0,0), ( x,graphicsOffset-(e[0]*tickHeight), keyWidth,e[2]*tickHeight));
			#fillColor
		pygame.draw.rect(Window, channelColor[e[3]][1], ( x+2,graphicsOffset-(e[0]*tickHeight)+2, keyWidth-4,e[2]*tickHeight-4));
#CONSTANTS:
NUMBER_OF_KEYS = 128;

#Midi Settings:
initMidiOut();
midiInputDevice, port_name = initMidiIn();
Song = midiFileChooser();
pattern = loadSongMidiPattern(Song)
score = convertPatternToScore(pattern)
patternRes = getPatternRes(pattern)

#Display Settings:
windowWidth=1280
windowHeight=600
WindowRes = (windowWidth, windowHeight)
keyWidth = getKeyWidth(windowWidth)
keyHeight = getKeyHeight(windowHeight, patternRes)

#Image Loading:
whiteKeyHeight = 80;
blackKeyHeight = 40;
whiteKey = loadKeyImage("WK.png", keyWidth, whiteKeyHeight)
whiteKeyP = loadKeyImage("WKP.png", keyWidth, whiteKeyHeight)
blackKey = loadKeyImage("BK.png", keyWidth, blackKeyHeight)
blackKeyP = loadKeyImage("BKP.png", keyWidth, blackKeyHeight)

#Midi graphics interaction setup:
tickTime = getTickTime(getPatternMPQN(pattern), patternRes)
tickHeight = getKeyHeight(windowHeight, patternRes)

#Game clock setup:
#This should be reducible:
clock = pygame.time.Clock()
startTime = time.time()*1000.0
currentTime = 0.0
oldTime = 0.0
speedFactor = 1.0
midiTick = 0
graphicsOffset = 0;

Window = createWindow((windowWidth, windowHeight), "Pyano", "icon.png")

#Channel Cloros:
channelColor = [[(200,200,250), (150,150,200)], [(200,250,200), (150,200,150)], [(250,200,200), (200,150,150)], [(250,250,200), (200,200,150)]]

#Key status array setup:
keys = numpy.zeros(NUMBER_OF_KEYS)

#Running state:
running = True;

try:
#Main Game Loop:
	while running:
		#Exit event:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			#Keyboard events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r:
					#ResetGame:
					startTime = time.time()*1000
					midiTick = 0
				if event.key == pygame.K_ESCAPE:
					running = False
				if event.key == pygame.K_LEFT:
					speedFactor = speedFactor-0.1
				if event.key == pygame.K_RIGHT:
					speedFactor = speedFactor+0.1
				if event.key == pygame.K_UP:
					midiTick = midiTick - (1000/(tickTime/1000.0)*spepedFactor);
				if event.key == pygame.K_DOWN:
					midiiTick = midiTick + (1000/(tickTime/1000.0)*speedFactor);
		#Midi Events:
		midiInput = getMidiInput(midiInputDevice)
		playMidiInput(midiInput)

		#UpdateClocks:
		currentTime = (time.time()*1000.0)-startTime
		midiTick = midiTick + (((currentTime-oldTime)/(tickTime/1000.0))*speedFactor)
		oldTime = currentTime	
		graphicsOffset=midiTick*tickHeight;
		
		#Display:
		drawBackground();
		drawNotes(score);	
		drawKeys(keys);
		#Update graphics:
		pygame.display.update()
		#Delta time
		clock.tick(60);
except KeyboardInterrupt:
	print("")
#Cleanup:
finally:
	#Close audio input
	midiInputDevice.close_port()
	#Close graphics:
	pygame.quit()
