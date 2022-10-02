import pygame
from constants import *

class SoundSystem():
	MAGICAL_SOUND_SHOWER = 0
	PASSING_BREEZE = 1
	SPLASH_WAVE = 2
	TESTAROSSA_AUTODRIVE = 3

	musics = [
			'soundtracks/01 Magical Sound Shower.mp3',
			'soundtracks/02 Passing Breeze.mp3',
			'soundtracks/03 Splash Wave.mp3',
			'soundtracks/Testarossa Autodrive.mp3'
	]
	seashore = 'soundtracks/seashore.mp3'
	lastwave = 'soundtracks/Last Wave.mp3'


	def __init__(self):
		pygame.mixer.init()
		self.current = -1

	def playSeashore(self):
		if(not SOUND):
			return
		pygame.mixer.music.load(SoundSystem.seashore)
		pygame.mixer.music.play(loops=-1)

	def playLastWave(self):
		if(not SOUND):
			return
		pygame.mixer.music.load(SoundSystem.lastwave)
		pygame.mixer.music.play(loops=-1)

	def playMusic(self,musicid=MAGICAL_SOUND_SHOWER, loop=True):
		if(not SOUND):
			return
			
		musicid = min(max(0, musicid), 3)
		if(musicid == self.current):
			return
		self.current = musicid

		pygame.mixer.music.load(SoundSystem.musics[musicid])
		if(loop):
			pygame.mixer.music.play(loops=-1)
		else:
			pygame.mixer.music.play()

	def stopMusic(self):
		pygame.mixer.music.stop()

