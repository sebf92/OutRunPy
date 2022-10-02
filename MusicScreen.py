import pygame,sys,random
from constants import *
from SoundSystem import *

class MusicScreen():
	MAGICAL_SOUND_SHOWER = 0
	PASSING_BREEZE = 1
	SPLASH_WAVE = 2

	mss_file = "./sprites/sound_magical_sound_shower.png"
	pb_file = "./sprites/sound_passing_breeze.png"
	sw_file = "./sprites/sound_splash_wave.png"

	vumeter_file = "./sprites/sound_vumeter.png" # 138_186

	images = None

	vumeter = None

	def __init__(self, soundsystem):
		if(MusicScreen.images == None):
			MusicScreen.images = list()
			img = pygame.image.load(MusicScreen.mss_file).convert()
			w = img.get_width()
			h = img.get_height()
			rw = WIDTH/w
			rh = HEIGHT/h
			img = pygame.transform.scale(img, (WIDTH, HEIGHT)) 
			MusicScreen.images.append(img)
			img = pygame.image.load(MusicScreen.pb_file).convert()
			img = pygame.transform.scale(img, (WIDTH, HEIGHT)) 
			MusicScreen.images.append(img)
			img = pygame.image.load(MusicScreen.sw_file).convert()
			img = pygame.transform.scale(img, (WIDTH, HEIGHT)) 
			MusicScreen.images.append(img)

			img:pygame.Surface = pygame.image.load(MusicScreen.vumeter_file).convert_alpha()
			MusicScreen.vumeter = list()
			for i in range(4):
				img1:pygame.Surface = img.subsurface(0, i*7, img.get_width(), 7)
				nw = round(46*rw)
				nh = round(7*rh)
				img1 = pygame.transform.scale(img1, (nw, nh)) 
				MusicScreen.vumeter.append(img1)
			
			self.vumeterRect = pygame.Rect(round(138*rw), round(186*rh), round(46*rw), round(7*rh))

		self.selection = MusicScreen.PASSING_BREEZE
		self.soundsystem:SoundSystem = soundsystem

		self.soundsystem.playMusic(self.selection)

	def run(self, screen:pygame.Surface):
		clock = pygame.time.Clock()
		next = False
		t = 0
		vumeterIndex = 0
		while not next:
			# FPS images per second
			elapsedtime = clock.tick(FPS)	
			t+=elapsedtime
			if(t>random.randint(100, 200)):
				t = 0
				vumeterIndex = random.randint(0, len(MusicScreen.vumeter)-1)

			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					pygame.quit()
					sys.exit(0)
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						next = True
					elif event.key == pygame.K_LEFT:
						self.selection -= 1
						self.selection = min(max(self.selection, 0), 2)
						self.soundsystem.playMusic(self.selection)
					elif event.key == pygame.K_RIGHT:
						self.selection += 1
						self.selection = min(max(self.selection, 0), 2)
						self.soundsystem.playMusic(self.selection)
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit(0)

			image = MusicScreen.images[self.selection]
			rect = pygame.Rect(0,0,image.get_width(), image.get_height())
			screen.blit(image, rect)

			screen.blit(MusicScreen.vumeter[vumeterIndex], self.vumeterRect)

			# screen update
			pygame.display.update()
			

