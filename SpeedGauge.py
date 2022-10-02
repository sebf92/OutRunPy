import pygame, math
from constants import *

class SpeedGauge(pygame.sprite.Sprite):
	GAUGESIZE = int(HEIGHT/5)
	TICKCOLOR = (255,0,0)

	tiles = pygame.image.load("./sprites/gauge.png")

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		SpeedGauge.tiles = SpeedGauge.tiles.convert_alpha()
		SpeedGauge.tiles = pygame.transform.smoothscale(SpeedGauge.tiles, (SpeedGauge.GAUGESIZE, SpeedGauge.GAUGESIZE)) 

		self.x = 0
		self.y = 0
		self.speed = 0
		self.image = pygame.Surface((SpeedGauge.GAUGESIZE, SpeedGauge.GAUGESIZE), pygame.SRCALPHA, 32).convert_alpha()
		self.rect = pygame.Rect(self.y,self.y,SpeedGauge.GAUGESIZE, SpeedGauge.GAUGESIZE)

	def update(self,time):
		self.image.fill((0,0,0,0))
		self.image.blit(SpeedGauge.tiles, (0,0))

		# draw needle
		startpos = (SpeedGauge.GAUGESIZE/2,SpeedGauge.GAUGESIZE/2)

		vibration = time%3-1

		angle = 250-self.speed+vibration
		if(angle<0):
			angle+=360
		xdest = SpeedGauge.GAUGESIZE/2+math.cos(angle*2*math.pi/360)*SpeedGauge.GAUGESIZE/2*0.7
		ydest = SpeedGauge.GAUGESIZE/2-math.sin(angle*2*math.pi/360)*SpeedGauge.GAUGESIZE/2*0.7
		endpos = (xdest,ydest)
		pygame.draw.line(self.image, SpeedGauge.TICKCOLOR, startpos, endpos, 4)

		self.image.set_alpha( 128 )

		self.rect = pygame.Rect(self.x,self.y,self.image.get_width(),self.image.get_height())

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def getSize(self):
		return SpeedGauge.GAUGESIZE

	def setSpeed(self, speed):
		speed = min(max(speed, 0), 300)
		self.speed = speed