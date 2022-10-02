import pygame
from constants import *

class Plant():
	PALMTREE = 0
	TREE1 = 1
	TREE2 = 2
	DEADTREE1 = 3
	DEADTREE2 = 4
	BUSH1 = 5
	BUSH2 = 6
	CACTUS = 7
	STUMP = 8
	BOULDER1 = 9
	BOULDER2 = 10
	BOULDER3 = 11
	WINDSURF1 = 12
	WINDSURF2 = 13
	WINDSURF3 = 14

	RATIO = 1

	tiles = None
	plantimages = None

	plantinfos = [	("palm tree", 1, 1, 215, 540),
					("tree1", 621, 1, 360, 360),
					("tree2", 1201, 1, 282, 295),
					("deadtree1", 1, 551, 135, 332),
					("deadtree2", 1201, 486, 150, 260),
					("bush1", 1, 1094, 240, 155),
					("bush2", 251, 1094, 232, 152 ),
					("cactus", 925, 894, 235, 118),
					("stump", 991, 326, 195, 140),
					("boulder1", 1201, 756, 168, 248),
					("boulder2", 617, 894, 298, 140),
					("boulder3", 226, 276, 320, 220)
				]

	levelinfos = [ 	("windsurf1", 922, 591, 51, 106),
					("windsurf2", 974, 591, 51, 106),
					("windsurf3", 1026, 591, 51, 106)
				]

	buffer = None

	imagecache = {}

	def __init__(self, type):

		if(Plant.buffer==None):
			Plant.buffer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32).convert_alpha()

		if(Plant.tiles == None):
			# Load tiles
			Plant.tiles = pygame.image.load("./sprites/plants.png")
			Plant.tiles = Plant.tiles.convert_alpha()
			imglist = list()
			for i in range(len(Plant.plantinfos)):
				(name,x,y,w,h) = Plant.plantinfos[i]
				img = Plant.tiles.subsurface(pygame.Rect(x, y, w, h))
				imglist.append(img)

			Plant.tiles = pygame.image.load("./sprites/spriteslvl1.png")
			Plant.tiles = Plant.tiles.convert_alpha()
			for i in range(len(Plant.levelinfos)):
				(name,x,y,w,h) = Plant.levelinfos[i]
				img = Plant.tiles.subsurface(pygame.Rect(x, y, w, h))
				img = pygame.transform.scale2x(img)
				imglist.append(img)

			Plant.plantimages = imglist


		self.roadsegment = None
		self.x = 0
		self.y = 0
		self.position = 0
		self.flip = False
		self.zoomfactor = 1
		type = min(max(0, type), len(Plant.plantimages)-1)
		self.type = type
		self.image = Plant.plantimages[type]
		self.rect = pygame.Rect(self.x-self.image.get_width()/2,self.y-self.image.get_height(), self.image.get_width(), self.image.get_height())

		self.repeatx = False

	def update(self, time, clipy:int):
		plant = Plant.plantimages[self.type]
		currentwidth = int(plant.get_width()*Plant.RATIO*self.zoomfactor)
		currentheight = int(plant.get_height()*Plant.RATIO*self.zoomfactor)

		x = self.x-currentwidth/2
		y = self.y-currentheight

		if(y>clipy): # sprite is clipped... don't draw
			self.image = None
			return
			
		clippedheight = currentheight
		if(y+currentheight>clipy): # sprite is partially clipped...
			clippedheight = clipy - y #clipped height
			if(clippedheight==0): # nothing left to draw...
				self.image = None
				return

		if(currentwidth>0 and currentheight>0 and currentwidth<WIDTH and currentheight<HEIGHT):
			key = str(self.type)+'.'+str(currentwidth)+'.'+str(currentheight)
			if(key in Plant.imagecache):
				scaledplant = Plant.imagecache[key]
			else:
				#scaledplant = Plant.buffer.subsurface(0, 0, currentwidth, currentheight) # scale the sprite
				#scaledplant.fill((0,0,0,0))
				scaledplant = pygame.transform.scale(plant, (currentwidth, currentheight)) 
				scaledplant.set_alpha( 255 )
				Plant.imagecache[key] = scaledplant
			if(clippedheight>0): #take only a subportion of the sprite... if needed
				scaledplant = scaledplant.subsurface(0, 0, currentwidth, clippedheight)
		else:
			scaledplant = None # skip drawing...
			return

		# flip image if needed
		if(self.flip and scaledplant!=None):
			scaledplant = pygame.transform.flip(scaledplant, True, False)

		self.image = scaledplant
		self.rect = pygame.Rect(x, y, currentwidth, clippedheight)

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setZoomFactor(self, zoomfactor):
		self.zoomfactor = zoomfactor

	def leftside(self):
		self.flip = True

	def setRoadSegment(self, position, segment):
		self.position = position
		self.roadsegment = segment
		self.roadsegment.addSprite(position, self)

	def doProjection(self):
		x1 = self.roadsegment.p1.screen.x
		y1 = self.roadsegment.p1.screen.y
		w1 = self.roadsegment.p1.screen.w
		r1 = self.roadsegment.rumbleWidth(w1, self.roadsegment.lanes)
		gap = self.roadsegment.gap
		offset = self.position

		if(gap>=10): # do not draw sprite if they are too far away
			return

		# compute sprites scales and position
		self.setZoomFactor(self.roadsegment.spritezoomfactor)
		if(offset<0):
			offset += 1
			self.setXY(x1-w1-r1*2+w1*offset/2, y1)
		elif(offset>0):
			offset -= 1
			offset += gap*2
			self.setXY(x1+w1+r1*2+w1*offset/2, y1)
		else:
			if(gap>=3): 
				self.setXY(x1+w1+r1*2+w1*offset/2+w1/8, y1)
			else:
				self.setXY(0,10000) # do not draw sprite if road overlap

	def isRepeating(self):
		return None
