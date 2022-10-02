import pygame,random
from constants import *
from RoadSegment import *

class Cars():
	SEMI = 0
	TRUCK = 1
	CAR03 = 2
	CAR02 = 3
	CAR04 = 4
	CAR01 = 5

	RIGHT = 0
	LEFT = 1

	RATIO = 0.65*WIDTH/640 # zoom the sprite depending in screen resolution...

	TRACKLENGTH = 0

	tiles = None
	carimages = None

	carinfos = [	("semi", 1361, 486, 122, 144),
					("truck", 1365, 639, 100, 78),
					("car03", 1379, 756, 88, 55),
					("car02", 1379, 821, 80, 59),
					("car04", 1379, 889, 80, 57),
					("car01", 1201, 1014, 80, 56)
				]

	buffer = None

	imagecache = {}

	def __init__(self, tracklen, type):

		if(Cars.buffer==None):
			Cars.buffer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32).convert_alpha()

		if(Cars.tiles == None):
			# Load tiles
			Cars.tiles = pygame.image.load("./sprites/plants.png")
			Cars.tiles = Cars.tiles.convert_alpha()
			imglist = list()
			for i in range(len(Cars.carinfos)):
				(name,x,y,w,h) = Cars.carinfos[i]
				img = Cars.tiles.subsurface(pygame.Rect(x, y, w, h))
				imglist.append(img)
			Cars.carimages = imglist

		Cars.TRACKLENGTH = tracklen
		self.x = 0 # screen coordinates
		self.y = 0

		self.roadsegment:RoadSegment = None
		self.position = 0 	# position on road -1<->1
		self.z = 0 			# position on road
		self.track = Cars.LEFT # set track 'left tack or right track)
		self.speed = 0		# current speed
		self.direction = Cars.RIGHT # turning left/right
		self.zoomfactor = 1
		self.rightTrackOffset = 0
		type = min(max(0, type), len(Cars.carimages)-1)
		self.type = type
		self.image = Cars.carimages[type]
		self.rect = pygame.Rect(self.x-self.image.get_width()/2,self.y-self.image.get_height(), self.image.get_width(), self.image.get_height())

	def update(self, clipy:int):
		car = Cars.carimages[self.type]
		currentwidth = int(car.get_width()*Cars.RATIO*self.zoomfactor)
		currentheight = int(car.get_height()*Cars.RATIO*self.zoomfactor)

		x = self.x-currentwidth/2
		y = self.y-currentheight

		if(self.track == Cars.RIGHT):
			x += self.rightTrackOffset

		if(Cars.RATIO*self.zoomfactor>0.5):
			y += random.randint(0,1)

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
			if(key in Cars.imagecache):
				scaledcar = Cars.imagecache[key]
			else:
				#scaledcar = Cars.buffer.subsurface(0, 0, currentwidth, currentheight) # scale the sprite
				#scaledcar.fill((0,0,0,0))
				scaledcar = pygame.transform.scale(car, (currentwidth, currentheight)) 
				scaledcar.set_alpha( 255 )
				Cars.imagecache[key] = scaledcar
			if(clippedheight>0): #take only a subportion of the sprite... if needed
				scaledcar = scaledcar.subsurface(0, 0, currentwidth, clippedheight)
		else:
			scaledcar = None # skip drawing...
			return

		# flip image if needed
		if(self.direction == Cars.LEFT and scaledcar!=None):
			scaledcar = pygame.transform.flip(scaledcar, True, False)

		self.image = scaledcar
		self.rect = pygame.Rect(x, y, currentwidth, clippedheight)

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setZoomFactor(self, zoomfactor):
		self.zoomfactor = zoomfactor

	def setRightTrackOffset(self, offset):
		self.rightTrackOffset = offset

	def setDirection(self, direction):
		self.direction = direction

	def setPosition(self, position):
		position = min(max(-1, position),1)
		self.position = position

	def setZ(self, z):
		self.z = z
		self.z = self.z % Cars.TRACKLENGTH

	def setSpeed(self, speed):
		self.speed = speed
	
	def setTrack(self, track):
		'''
		LEFT
		RIGHT
		'''
		self.track = track

	def move(self):
		self.z += self.speed
		self.z = self.z % Cars.TRACKLENGTH

	def doProjection(self, direction = RIGHT):
		z = self.z%self.roadsegment.SEGMENTLENGTH
		ratio = z/self.roadsegment.SEGMENTLENGTH

		# on fait une simple interpolation lineaire entre les deux segments pour trouver la position de la voiture
		xscreen = self.roadsegment.p1.screen.x + (self.roadsegment.p2.screen.x-self.roadsegment.p1.screen.x)*ratio
		wscreen = self.roadsegment.p1.screen.w + (self.roadsegment.p2.screen.w-self.roadsegment.p1.screen.w)*ratio
		yscreen = self.roadsegment.p1.screen.y + (self.roadsegment.p2.screen.y-self.roadsegment.p1.screen.y)*ratio
		zoomfactor = self.roadsegment.previoussegment.spritezoomfactor + (self.roadsegment.spritezoomfactor-self.roadsegment.previoussegment.spritezoomfactor)*ratio

#			(x, y) = self.projectCoordinates(0, yworld, car.z, cameraX-curve, cameraY, cameraZ, cameraDepth, width, height, roadWidth)
		self.x = xscreen + self.position*wscreen
		self.y = yscreen
		self.setZoomFactor(zoomfactor)
		self.setRightTrackOffset(wscreen*self.roadsegment.gap)
		self.setDirection(direction)

	def setRoadSegment(self, segment):
		if(segment == self.roadsegment): 	# same segment, skip
			return
		if(self.roadsegment!=None):  		# new segment, move from the old on to the new one
			self.roadsegment.removeCar(self)
		self.roadsegment = segment
		self.roadsegment.addCar(self)

	def isColliding(self, xpos):
		xpos += 10 # ensure a value >0
		if(self.track == Cars.LEFT):
			realposition = 10 + self.position
		else:
			realposition = 10 + self.position + self.roadsegment.gap

		if(abs(xpos-realposition)<0.2):
			return True
		else:
			return False
