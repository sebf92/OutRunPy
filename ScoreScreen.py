import pygame,sys
from constants import *
from SoundSystem import *

class ScoreScreen():
	img = "./sprites/high_score.png"

	def __init__(self, soundsystem):
		self.soundsystem:SoundSystem = soundsystem
		self.image = pygame.image.load(ScoreScreen.img).convert()
		ratio = WIDTH/self.image.get_width()
		w = int(WIDTH)
		h = int(self.image.get_height() * ratio)
		self.image = pygame.transform.smoothscale(self.image, (w, h)) 
		self.rect = pygame.Rect(WIDTH/2-w/2,HEIGHT/2-h/2,w,h)
		self.soundsystem.playLastWave()


	def run(self, screen:pygame.Surface):
		clock = pygame.time.Clock()
		next = False
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

			screen.blit(self.image, self.rect)

			# screen update
			pygame.display.update()
			

