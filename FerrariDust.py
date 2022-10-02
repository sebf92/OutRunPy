from msilib import sequence
import pygame, random, math
from Ferrari import Ferrari
from constants import *

class FerrariDust():
	SMOKE = 0
	DUST = 1

	tiles = pygame.image.load("./sprites/effectsCar.png")

	sequences = [
		("smoke", [0,1,2,3,4,5,6,7]),
		("dust", [8,9,10,11,12,13,14,15])
	]

	coordinates = [
		("smoke1", 1, 1, 58, 17),
		("smoke2", 60, 1, 58, 17),
		("smoke3", 119, 1, 58, 17),
		("smoke4", 178, 1, 58, 17),
		("smoke5", 237, 1, 58, 17),
		("smoke6", 296, 1, 58, 17),
		("smoke7", 355, 1, 58, 17),
		("smoke8", 414, 1, 58, 17),
		("dust1", 1, 19, 68, 42),
		("dust2", 70, 19, 68, 42),
		("dust3", 139, 19, 68, 42),
		("dust4", 208, 19, 68, 42),
		("dust5", 277, 19, 68, 42),
		("dust6", 346, 19, 68, 42),
		("dust7", 415, 19, 68, 42),
		("dust8", 484, 19, 68, 42)
	]

	allimages = None

	def __init__(self, type):

		FerrariDust.tiles = FerrariDust.tiles.convert_alpha()
		self.x = 0
		self.y = 0
		self.carwidth = 10

		self.timecounter = 0
		self.sequenceindex = 0
		self.type = type

		self.initImages()

	def initImages(self):
		FerrariDust.allimages = list()
		for (name, x, y, w, h) in FerrariDust.coordinates:
			FerrariDust.allimages.append(self.getImage(FerrariDust.tiles, pygame.Rect(x,y,w,h)))


	def getImage(self, tiles:pygame.Surface, rect:pygame.Rect):
		img = tiles.subsurface(rect).convert_alpha()

		w = img.get_width()
		h = img.get_height()

		carw = self.carwidth
		carh = (h*carw)/w

		sw = int(carw)
		sh = int(carh)
		img = pygame.transform.scale(img, (sw, sh)) 
		return img

	def update(self,time):
		(name,sequence) = FerrariDust.sequences[self.type]

		self.timecounter += time
		if(self.timecounter>100):
			self.timecounter -= 100
			self.sequenceindex+=1
			self.sequenceindex = self.sequenceindex%len(sequence)

		self.image = FerrariDust.allimages[sequence[self.sequenceindex]]
		self.rect = pygame.Rect(self.x-self.image.get_width()/2,self.y-self.image.get_height(), self.image.get_width(), self.image.get_height())

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setCarWidth(self, carwidth):
		if(self.carwidth != carwidth):
			self.carwidth = carwidth
			self.initImages()
