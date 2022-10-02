import pygame,sys
from constants import *
from SoundSystem import *

class SplashScreen():
	img = "./sprites/splashscreen_foreground.png"
	bck = "./sprites/splashscreen_background.png"

	foreground = None
	foreground_rect = None
	background = None

	def __init__(self, soundsystem):
		self.soundsystem:SoundSystem = soundsystem
		img = pygame.image.load(SplashScreen.img).convert_alpha()
		ratio = WIDTH/img.get_width()
		w = int(WIDTH)
		h = int(img.get_height() * ratio)
		SplashScreen.foreground = pygame.transform.smoothscale(img, (w, h)) 
		SplashScreen.foreground_rect = pygame.Rect(WIDTH/2-w/2,HEIGHT/2-h/2,w,h)

		bck = pygame.image.load(SplashScreen.bck).convert()
		w = int(bck.get_width()*ratio)
		h = int(bck.get_height()*ratio)
		SplashScreen.background = pygame.transform.smoothscale(bck, (w, h)) 

		self.soundsystem.playSeashore()


	def run(self, screen:pygame.Surface):
		clock = pygame.time.Clock()
		next = False
		xinit = 0
		while not next:
			# FPS images per second
			elapsedtime = clock.tick(FPS)	

			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					pygame.quit()
					sys.exit(0)
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						next = True
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit(0)

			# scroll the background tiles
			x = xinit
			while(x<WIDTH):
				screen.blit(SplashScreen.background, pygame.Rect(x,HEIGHT/2-SplashScreen.background.get_height()/2,SplashScreen.background.get_width(), SplashScreen.background.get_height()))
				x += SplashScreen.background.get_width()
			xinit -= 1
			if(abs(xinit)>SplashScreen.background.get_width()):
				xinit = 0

			# foreground title
			screen.blit(SplashScreen.foreground, SplashScreen.foreground_rect)

				
			# screen update
			pygame.display.update()
			

