from urllib.parse import ParseResultBytes
import pygame
from constants import *
from RoadSegment import * 

class Ferrari(pygame.sprite.Sprite):
	MAXSPEED = 290								# top speed (ensure we can't move more than 1 segment in a single frame to make collision detection easier)
	ACCEL =MAXSPEED/(FPS*6)						# acceleration rate - 6 seconds to max speed
	BREAKING = -MAXSPEED/(FPS*2)				# deceleration rate when braking
	DECEL = -MAXSPEED/(FPS*15)					# 'natural' deceleration rate when neither accelerating, nor braking
	OFFROAD = -MAXSPEED/(FPS*3)					# 'offroad' deceleration
	ACCIDENT = -MAXSPEED/(FPS/2)				# acceleration rate when accident

	tiles = pygame.image.load("./sprites/ferrariArcade.png")
	tilesBreak = pygame.image.load("./sprites/ferrariArcadeBreak.png")

	DIRECTION_LEFT2 = -2
	DIRECTION_LEFT1 = -1
	DIRECTION_STRAIGHT = 0
	DIRECTION_RIGHT1 = 1
	DIRECTION_RIGHT2 = 2

	SLOPE_UP = 2
	SLOPE_MIDDLE = 7
	SLOPE_DOWN = 12


	ferrariImages = None
	ferrariBreakImages = None
	ferrariAccidentImages = None

	sequences = [
		("upleft2", [0, 5, 10, 15]),
		("upleft1", [1, 6, 11, 16]),
		("up", [2, 7, 12, 17]),
		("upright1", [3, 8, 13, 18]),
		("upright2", [4, 9, 14, 19]),
		("middleleft2", [20, 25, 30, 35]),
		("middleleft1", [21, 26, 31, 36]),
		("middle", [22, 27, 32, 37]),
		("middleright1", [23, 28, 33, 38]),
		("middleright2", [24, 29, 34, 39]),
		("downleft2", [40, 45, 50, 55]),
		("downleft1", [41, 46, 51, 56]),
		("down", [42, 47, 52, 57]),
		("downright1", [43, 48, 53, 58]),
		("downright2", [44, 49, 54, 59])
	]

	accidentSequence = [
		0, 1, 2, 3, 4, 5, 6, 7,
		8, 9,
		8, 9,
		8, 9,
		8, 9,
		8, 9,
		8, 9,
		8, 9,
		8, 9,
	]

	zoomaccident = 1.6
	accident_coord = [
		(zoomaccident, 481, 1, 171, 46),
		(zoomaccident, 653, 1, 171, 46),
		(zoomaccident, 481, 48, 171, 46),
		(zoomaccident, 653, 48, 171, 46),
		(zoomaccident, 481, 95, 171, 46),
		(zoomaccident, 653, 95, 171, 46),
		(zoomaccident, 481, 142, 171, 46),
		(zoomaccident, 653, 142, 171, 46),
		(zoomaccident, 481, 236, 171, 46),
		(zoomaccident, 653, 236, 171, 46),
	]

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		Ferrari.tiles = Ferrari.tiles.convert_alpha()
		Ferrari.tilesBreak = Ferrari.tilesBreak.convert_alpha()
		self.currentDirection = Ferrari.DIRECTION_STRAIGHT
		self.currentSlope = Ferrari.SLOPE_MIDDLE
		self.sequenceindex = 0
		self.timecounter = 0

		self.roadsegment:RoadSegment = None

		self.speed = 0
		self.acceleration = False
		self.breaking = False
		self.isoffroad = False
		self.isAccident = False
		self.accidentSequenceIndex = 0

		self.carwidth = 10
		self.x = 0
		self.y = 0
		self.image = None
		self.rect = pygame.Rect(self.x,self.y,95,44)
		self.initImages()

	def initImages(self):
		# Car
		sequence = list()
		sequenceBreak = list()
		carWidth = 95
		carHeight = 44
		xgap = 1
		ygap = 1
		for i in range(60):
			xrange = i%5
			yrange = i//5
			x = xgap+xrange*(carWidth+xgap)
			y = ygap+yrange*(carHeight+ygap)
			sequence.append(self.getImage(Ferrari.tiles, pygame.Rect(x,y,carWidth,carHeight)))
			sequenceBreak.append(self.getImage(Ferrari.tilesBreak, pygame.Rect(x,y,carWidth,carHeight)))
		Ferrari.ferrariImages = sequence
		Ferrari.ferrariBreakImages = sequenceBreak

		# Accident
		sequence = list()
		for (ratio, x,y,w,h) in Ferrari.accident_coord:
			sequence.append(self.getImage(Ferrari.tiles, pygame.Rect(x,y,w,h), ratio))
		Ferrari.ferrariAccidentImages = sequence

	def getImage(self, tiles, rect, ratio=1):
		img = tiles.subsurface(rect).convert_alpha()

		w = img.get_width()
		h = img.get_height()

		ratiow = ratio
		ratioh = ratio
		if(ratio!=1):
			ratioh = ratio / 1.3

		carw = ratiow * self.carwidth
		carh = ratioh * (h*carw)/w

		sw = int(carw)
		sh = int(carh)
		img = pygame.transform.scale(img, (sw, sh)) 
		return img

	def setSlope(self, ydirection):
		'''
		UP
		MIDDLE
		DOWN
		'''
		ydirection = min(max(ydirection, Ferrari.SLOPE_UP), Ferrari.SLOPE_DOWN)
		self.currentSlope = ydirection

	def setDirection(self, xdirection):
		'''
		LEFT2
		LEFT1
		STRAIGHT
		RIGHT1
		RIGHT2
		'''
		xdirection = min(max(xdirection, Ferrari.DIRECTION_LEFT2), Ferrari.DIRECTION_RIGHT2)
		self.currentDirection = xdirection

	def update(self, time):
		if(self.isAccident):
			self.updateAccident(time)
		else:
			self.updateDrive(time)

	def updateAccident(self,time):
		self.speed += Ferrari.ACCIDENT
		self.speed = min(max(self.speed, 0), Ferrari.MAXSPEED)

		imageIndex = Ferrari.accidentSequence[self.accidentSequenceIndex]
		self.image = Ferrari.ferrariAccidentImages[imageIndex]
		self.rect = pygame.Rect(self.x-self.image.get_width()/2,self.y-self.image.get_height(), self.image.get_width(), self.image.get_height())
		
		self.timecounter += time
		if(self.timecounter>100):
			self.timecounter -= 100
			self.accidentSequenceIndex += 1
			self.accidentSequenceIndex = self.accidentSequenceIndex%len(Ferrari.accidentSequence)
			if(self.accidentSequenceIndex==0):
				self.isAccident = False


	def updateDrive(self,time):
		if(self.isoffroad==True and self.speed>50):
			self.speed += Ferrari.OFFROAD

		if(self.breaking==True):
			self.speed += Ferrari.BREAKING
		elif(self.acceleration==True):
			self.speed += Ferrari.ACCEL
		else:
			self.speed += Ferrari.DECEL
		self.speed = min(max(self.speed, 0), Ferrari.MAXSPEED)

		index = self.currentSlope + self.currentDirection
		(directionstr, sequence) = Ferrari.sequences[index]
		self.sequenceindex = self.sequenceindex%len(sequence) # just in case...
		imageindex = sequence[self.sequenceindex]
		if(self.breaking==True):
			self.image = Ferrari.ferrariBreakImages[imageindex]
		else:
			self.image = Ferrari.ferrariImages[imageindex]

		self.timecounter += time
		if(self.timecounter>100):
			self.timecounter -= 100
			if(self.speed==0):
				pass # skip animation
			elif(self.speed<100):
				self.sequenceindex+=2 # animation (skip moving hairs)
			else:
				self.sequenceindex+=1 # animation
			self.sequenceindex = self.sequenceindex%len(sequence)

		if(self.speed==0):
			vibration = 0
		else:
			vibration = time%3-1
		self.rect = pygame.Rect(self.x-self.image.get_width()/2,self.y-self.image.get_height()+vibration, self.image.get_width(), self.image.get_height())

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setCarWidth(self, carwidth):
		if(self.carwidth != carwidth):
			self.carwidth = carwidth
			self.initImages()

	def setRoadSegment(self, segment:RoadSegment):
		if(segment == self.roadsegment): 	# same segment, skip
			return

		# manage car y direction based on the slope
		self.roadsegment = segment
		slope = (self.roadsegment.p2.world.y-self.roadsegment.p1.world.y)
		if(slope>0):
			self.currentSlope = Ferrari.SLOPE_UP
		elif(slope<0):
			self.currentSlope = Ferrari.SLOPE_DOWN
		else:
			self.currentSlope = Ferrari.SLOPE_MIDDLE

	def setAcceleration(self, acceleration):
		'''
		acceleration = Boolean
		'''
		self.acceleration = acceleration

	def getAcceleration(self):
		return self.acceleration

	def isAccelerating(self):
		return self.acceleration

	def setBreaking(self, breaking):
		self.breaking = breaking

	def isBreaking(self):
		return self.breaking

	def getSpeed(self):
		return int(self.speed)

	def offroad(self, isoffroad):
		self.isoffroad = isoffroad

	def accident(self):
		if(not self.isAccident):
			self.isAccident = True
			self.accidentSequenceIndex = 0		
			self.timecounter = 0
		
	def isAccidented(self):
		return self.isAccident