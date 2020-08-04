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


#Set up midi input
try:
	midiin, port_name = open_midiinput(1)
except:
	print("Midi error")

#sets up midi output:
try:
	fluidsynth.init('Piano.sf2',"alsa")
except:
	print("Midi output fail")
#Load midi file:
#If more then one argument load the second one as midi patter:
MIDIres=0
#Choose file:
r = Tk()
r.filename = filedialog.askopenfilename(initialdir = "",title ="Select a MIDI file" , filetypes = (("MIDI", "*.mid"),("All files", "*")))
Song=os.path.relpath(r.filename)
r.destroy()
try:
	pattern = midi.read_midifile(Song)
	MIDIres= pattern.resolution
	SongName = str(Song)
	pattern.make_ticks_abs()
except:
	print("Failed to load midi pattern")
p = numpy.concatenate(pattern)
#Timing:
notes = []
TPQN=24;
BPM=120
MPQN=60000
#Strip to just notes:
for e in p:
	if "TimeSignature" in str(e):
		#Ticks per quarter note
		TPQN = e.get_metronome()
	if "SetTempo" in str(e):
		BPM = e.get_bpm()
		MPQN = e.get_mpqn()
	if "Note" in str(e):
		eventType = 0
		if "NoteOn" in str(e):
			eventType = 1
			if e.get_velocity == 0:
				eventType = 0;
		#Note format
		notes.append([e.tick, e.get_pitch(), eventType, e.channel])
tickTime = MPQN/MIDIres;
#Conver to non retard format:
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
score = sorted(score, key=itemgetter(0))
#Display settings:
w=1280
h=600
#Key status array setup:
nuOfKeys = 128;
keys = numpy.zeros(nuOfKeys)
#Dimentions scaling setup:
keySize = int(w/(nuOfKeys/12*7))
#Image Loading:
whiteKey = pygame.image.load("WK.png")
whiteKey = pygame.transform.scale(whiteKey,(keySize, 80))
blackKey = pygame.image.load("BK.png")
blackKey = pygame.transform.scale(blackKey,(keySize, 40))
whiteKeyP = pygame.image.load("WKP.png")
whiteKeyP = pygame.transform.scale(whiteKeyP,(keySize, 80))
blackKeyP = pygame.image.load("BKP.png")
blackKeyP = pygame.transform.scale(blackKeyP,(keySize, 40))
w=int(keySize*(nuOfKeys/12*6))
resolution = (w,h)
#Game clock setup:
clock = pygame.time.Clock()
sms = time.time()*1000.0
ms = 0
msOld = 0
factor = 1.0
tick = 0
y=0;
tickRes=h/MIDIres/10
#Running state:
running = True;
#Sets up graphics:
icon = pygame.image.load("icon.png")
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption('Pyano')
pygame.display.set_icon(icon);
#Channel Cloros:
channelColor = [[(200,200,250), (150,150,200)], [(200,250,200), (150,200,150)], [(250,200,200), (200,150,150)], [(250,250,200), (200,200,150)]]
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
					sms = time.time()*1000
					tick = 0
				if event.key == pygame.K_ESCAPE:
					running = False
				if event.key == pygame.K_LEFT:
					factor = factor-0.1
				if event.key == pygame.K_RIGHT:
					factor = factor+0.1
				if event.key == pygame.K_UP:
					tick = tick - (1000/(tickTime/1000.0)*factor);
				if event.key == pygame.K_DOWN:
					tick = tick + (1000/(tickTime/1000.0)*factor);
		#Gets midi input
		msg= midiin.get_message()
		if msg:
			key = int(msg[0][1])
			keys[key] = not keys[key]
			fluidsynth.play_Note(key, 0, keys[key]*100)	
		#Logic
		#Calculate Ticks:
		ms = (time.time()*1000.0)-sms
		tick = tick + (((ms-msOld)/(tickTime/1000.0))*factor);
		msOld = ms	
		#Note Position Displacement:
		y=tick*tickRes;
		#Display:
		#clear screen:
		#Background:
		screen.fill((80,80,80))
		#Lines:
		for i in range(0, int(nuOfKeys/7)):
			pygame.draw.rect(screen, (250,250,250), ( i*keySize*7,0, 1,h));
			pygame.draw.rect(screen, (150,150,150), ( i*keySize*7+(keySize*3),0, 1,h));
		#Note Draw:
		for e in score:
			t = e[1]%12
			octave=int(e[1]/12)
			x=octave*7*keySize
			#White notei:
			if t not in [1,3,6,8,10]:
				if t in [0,2,4]:
					x=x+t/2*keySize
				if t in [5]:
					x=x+3*keySize
				if t in [7,9,11]:
					x=x+(t+1)/2*keySize
				#border
				pygame.draw.rect(screen, (0,0,0), ( x,y-(e[0]*tickRes), keySize,e[2]*tickRes));
				#fillColor
				pygame.draw.rect(screen, channelColor[e[3]][0], ( x+2,y-(e[0]*tickRes)+2, keySize-4,e[2]*tickRes-4));
			#black keys
			else:
				if t in [1,3]:
					x=x+int(t/2)*keySize+(keySize/2)
				if t in [6,8,10]:
					x=x+(t/2)*keySize+keySize/2
				#border
				pygame.draw.rect(screen, (0,0,0), ( x,y-(e[0]*tickRes), keySize,e[2]*tickRes));
				#fillColor
				pygame.draw.rect(screen, channelColor[e[3]][1], ( x+2,y-(e[0]*tickRes)+2, keySize-4,e[2]*tickRes-4));
		#White Keys:
		c=0
		for i in range(0,nuOfKeys):
			if( i%12 not in [1,3,6,8,10] ):
				if not keys[i]:
					screen.blit(whiteKey, (c,h-80));
				else:
					screen.blit(whiteKeyP, (c,h-80));
				c=c+keySize
		#Black Keys:
		c=keySize/2
		for i in range(0,nuOfKeys):
			if( i%12 in [1,3,6,8,10] ):
				if not keys[i]:
					screen.blit(blackKey, (c,h-80));
				else:
					screen.blit(blackKeyP, (c,h-80));
				c=c+keySize
			if (i%12 in [3, 10]):
				c=c+keySize
		#Update graphics:
		pygame.display.update()
		#Delta time
		clock.tick(60);
except KeyboardInterrupt:
	print("")
#Cleanup:
finally:
	#Close audio input
	midiin.close_port()
	#Close graphics:
	pygame.quit()
