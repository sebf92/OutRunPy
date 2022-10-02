# sources of inspiration
# http://www.extentofthejam.com/pseudo/
# https://codeincomplete.com/articles/javascript-racer/
# https://github.com/Guriva/Outrun

import pygame, math, random

from constants import *
from RoadSegment import RoadSegment
from Cars import Cars
from Plants import Plant
from Side import Side

class Road(pygame.sprite.Sprite):
	SEGMENTLENGTH  = 200 			# length of a single segment
	RUMBLELENGTH = 3				# number of segments per red/white rumble strip
	TRACKLENGTH =  0				# z length of entire track (computed at init)
	DRAWDISTANCE = 150 				# number of segments to draw
	LAYOUTDRAWDISTANCE = 150		# number of sprite segments to draw
	FIELDOFVIEW = 100				# angle (degrees) for field of view
	CAMERAHEIGHT = 1000				# z height of camera
	CAMERADEPTH = 1 / math.tan((FIELDOFVIEW/2) * math.pi/180) # z distance camera is from screen
	PLAYERZ = int(CAMERAHEIGHT * CAMERADEPTH) # player relative z distance from camera
	RESOLUTION = HEIGHT/480			# scaling factor to provide resolution independence
	FOGDENSITY = 5					# exponential fog density

	ROADWIDTH = 800					# actually half the roads width, easier math if the road spans from -roadWidth to +roadWidth
	LANES = 3						# number of lanes
	MAXSPEED = 290					# top speed (ensure we can't move more than 1 segment in a single frame to make collision detection easier)

	CENTRIFUGAL = 0.015				# centrifugal force multiplier when going around curves

	SKYCOLOR = "#72D7EE"			# Color of the sky

	ROADLENGTH_NONE = 0				# road section length in number of road segments
	ROADLENGTH_SHORT = 25
	ROADLENGTH_MEDIUM = 50
	ROADLENGTH_LONG = 100
	
	ROADCURVE_NONE = 0				# road curve
	ROADCURVE_EASY = 2
	ROADCURVE_MEDIUM = 4
	ROADCURVE_HARD = 6
	
	ROADHILL_NONE = 0				# road hill
	ROADHILL_LOW = 20
	ROADHILL_MEDIUM = 40
	ROADHILL_HIGH = 60

	background = None

	def __init__(self) -> None:
		pygame.sprite.Sprite.__init__(self)
		if(Road.background == None):
			Road.background = pygame.image.load("./sprites/background.png").convert()

		# create an image which is equivalent to the size of the screen
		self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
		self.rect = pygame.Rect(0,0,WIDTH,HEIGHT)

		self.previoushill = Road.ROADHILL_NONE # variable used during init
		self.previousgap = 3 # variable used during init
		self.tracksegments:list[RoadSegment] = []  # All road segments
		self.createTrack() # create the full track

		self.playerx = 0			# current player x position
		self.position = 0			# current camera position (z)
		self.speed = 0				# current speed

		self.direction = 0			# used for background scrolling
		self.lastsegment = None		# used for background scrolling

	def easeIn(self, a, b, percent):
		'''
		used to enter a curve smoothly
		'''
		return a + (b-a)*pow(percent,2)
	
	def easeOut(self, a, b, percent):
		'''
		used to exit a curve smoothly
		'''
		return a + (b-a)*(1-pow(1-percent,2))
	
	def easeInOut(self, a ,b ,percent):
		'''
		used to enter and exit a curve smoothly
		'''
		return a + (b-a)*((-math.cos(percent*math.pi)/2) + 0.5)

	def percentRemaining(self, n, total):
		'''
		utilities
		'''
		return (n%total)/total

	def interpolate(self, a ,b ,percent):
		'''
		utilities
		'''
		return a + (b-a)*percent

	def addSegment(self, curve, elevation, gap):
		'''
		Add a new road segment
		'''
		n = len(self.tracksegments)
		segmentcolor = RoadSegment.LIGHT if (n//Road.RUMBLELENGTH)%2==0 else RoadSegment.DARK # computing the sidewalk color
		segment = RoadSegment(n, elevation, n * Road.SEGMENTLENGTH, elevation, (n+1) * Road.SEGMENTLENGTH, curve, segmentcolor, Road.SEGMENTLENGTH, Road.LANES)
		segment.gap = gap #TODO integrer dans le constructeur
		self.tracksegments.append(segment)

	def addRoadSection(self, enter, hold, leave, curve, startelevation, endelevation, startgap, endgap):
		'''
		Add a new road section, including a curve if needed
		'''
		starty = startelevation * Road.SEGMENTLENGTH
		endy = endelevation * Road.SEGMENTLENGTH
		total = enter + hold + leave
		for n in range(enter):
			self.addSegment(self.easeIn(0, curve, n/enter), self.easeInOut(starty, endy, n/total), self.easeInOut(startgap, endgap, n/total))
		for n in range(hold):
			self.addSegment(curve, self.easeInOut(starty, endy, (n+enter)/total), self.easeInOut(startgap, endgap, (n+enter)/total))
		for n in range(leave):
			self.addSegment(self.easeOut(curve, 0, n/leave), self.easeInOut(starty, endy, (n+enter+hold)/total), self.easeInOut(startgap, endgap, (n+enter+hold)/total))
		

	def addRoadStraight(self, size = ROADLENGTH_MEDIUM, elevation = ROADHILL_NONE, gap = 0):
		self.addRoadSection(size, size, size, Road.ROADCURVE_NONE, self.previoushill, elevation, self.previousgap, gap)
		self.previoushill = elevation
		self.previousgap = gap

	def addRoadCurve(self, size = ROADLENGTH_MEDIUM, curve = ROADCURVE_MEDIUM, elevation = ROADHILL_NONE, gap = 0):
		self.addRoadSection(size, size, size, curve, self.previoushill, elevation, self.previousgap, gap)
		self.previoushill = elevation
		self.previousgap = gap

	def addRoadHill(self, size = ROADLENGTH_MEDIUM, elevation = ROADHILL_MEDIUM, gap = 0):
		self.addRoadSection(size, size, size, 0, self.previoushill, elevation, self.previousgap, gap)
		self.previoushill = elevation
		self.previousgap = gap

	def createTrack(self):
		'''
		INTERNAL METHOD
		Init a track made of a series of road segments
		'''
		self.addRoadStraight(Road.ROADLENGTH_LONG, Road.ROADHILL_NONE, 3)
		self.addRoadStraight(Road.ROADLENGTH_LONG, Road.ROADHILL_NONE, 3)
		self.addRoadStraight(Road.ROADLENGTH_LONG, Road.ROADHILL_NONE, 3)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, Road.ROADHILL_MEDIUM, 3)

		self.addRoadStraight(Road.ROADLENGTH_MEDIUM, Road.ROADHILL_HIGH,1.4)

		self.addRoadHill(Road.ROADLENGTH_MEDIUM, Road.ROADHILL_NONE,1.4)

		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, Road.ROADHILL_MEDIUM,1.4)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,   Road.ROADCURVE_MEDIUM, Road.ROADHILL_NONE,1.4)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,   Road.ROADCURVE_EASY, -Road.ROADHILL_HIGH,1.4)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, Road.ROADHILL_NONE,1.4)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_MEDIUM,1.4)

		self.addRoadStraight(Road.ROADLENGTH_LONG, Road.ROADHILL_HIGH,0.7)

		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  Road.ROADCURVE_MEDIUM, Road.ROADHILL_MEDIUM,0.7)
		self.addRoadCurve(Road.ROADLENGTH_LONG,  Road.ROADCURVE_MEDIUM, -Road.ROADHILL_HIGH,0.7)

		self.addRoadStraight(Road.ROADLENGTH_MEDIUM, -Road.ROADHILL_HIGH)

		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, Road.ROADHILL_NONE)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,   Road.ROADCURVE_MEDIUM, Road.ROADHILL_LOW)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,   Road.ROADCURVE_EASY, Road.ROADHILL_HIGH)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, -Road.ROADHILL_LOW)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_MEDIUM, Road.ROADHILL_LOW)

		self.addRoadCurve(Road.ROADLENGTH_LONG,  -Road.ROADCURVE_MEDIUM, Road.ROADHILL_MEDIUM,3)
		self.addRoadCurve(Road.ROADLENGTH_LONG,  Road.ROADCURVE_MEDIUM, Road.ROADHILL_LOW,3)

		self.addRoadStraight(Road.ROADLENGTH_MEDIUM, Road.ROADHILL_NONE,3)

		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, Road.ROADHILL_NONE)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,   Road.ROADCURVE_MEDIUM, Road.ROADHILL_LOW)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,   Road.ROADCURVE_EASY, Road.ROADHILL_HIGH)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_EASY, -Road.ROADHILL_LOW)
		self.addRoadCurve(Road.ROADLENGTH_MEDIUM,  -Road.ROADCURVE_MEDIUM, Road.ROADHILL_LOW)

		self.addRoadCurve(Road.ROADLENGTH_LONG,   -Road.ROADCURVE_EASY, Road.ROADHILL_NONE)
		self.addRoadStraight(Road.ROADLENGTH_LONG, Road.ROADHILL_NONE, 3)

		Road.TRACKLENGTH = len(self.tracksegments) * Road.SEGMENTLENGTH

		self.linkSegments()

		# test ... add some palm trees...
		for i in range(0, 50):
			side = Side(Side.GRANDSTAND)
			side.setLeftRight(Side.LEFT)
			side.setRoadSegment(-1, self.tracksegments[i])

		for i in range(50, 100, 10):
			plant = Plant(Plant.BUSH2)
			plant.leftside()
			plant.setRoadSegment(-1, self.tracksegments[i])
			plant = Plant(random.randint(1,11))
			plant.setRoadSegment(-random.randint(2,6), self.tracksegments[i])

		for i in range(100, 800):
			side = Side(Side.WATER)
			side.setLeftRight(Side.LEFT)
			side.setRoadSegment(-1, self.tracksegments[i])
			self.tracksegments[i].LFOGCOLOR = pygame.Color("#83E6C5")
		for i in range(120, 780, 20):
			plant = Plant(random.randint(12,14)) #windsurd
			plant.setRoadSegment(-random.randint(2,10), self.tracksegments[i])

		for i in range(0, 800, 10):
			plant = Plant(random.randint(1,11))
			plant.setRoadSegment(random.randint(2,6), self.tracksegments[i])

		for i in range(800, len(self.tracksegments), 10):
			plant = Plant(Plant.PALMTREE)
			plant.leftside()
			plant.setRoadSegment(-1, self.tracksegments[i])
			plant = Plant(random.randint(1,11))
			plant.setRoadSegment(random.randint(2,6), self.tracksegments[i])
			plant = Plant(random.randint(1,11))
			plant.setRoadSegment(-random.randint(2,6), self.tracksegments[i])

		for i in range(0, len(self.tracksegments), 10):
			plant = Plant(Plant.PALMTREE)
			plant.setRoadSegment(1, self.tracksegments[i])
			plant = Plant(Plant.BUSH1)
			plant.setRoadSegment(0, self.tracksegments[i])

		for i in range(3000, 5000):
			side = Side(Side.SAND)
			side.setLeftRight(Side.RIGHT)
			side.setRoadSegment(1, self.tracksegments[i])

	def linkSegments(self):
		'''
		internal use
		Links all road segments together to build an infinite (loop) list
		'''
		nbsegments = len(self.tracksegments)
		for i in range(nbsegments):
			index1 = (i-1)
			if(index1<0):
				index1 = nbsegments+index1
			index2 = i
			index3 = (i+1)%nbsegments

			segment1:RoadSegment = self.tracksegments[index1]
			segment2:RoadSegment = self.tracksegments[index2]
			segment3:RoadSegment = self.tracksegments[index3]

			segment2.setPrevious(segment1)
			segment2.setNext(segment3)

	def findSegment(self, z):
		'''
		returns the segment corresponding to the z position in the track
		'''
		return self.tracksegments[(z//Road.SEGMENTLENGTH) % len(self.tracksegments)]
	
	def update(self,time):
		'''
		rendering
		'''

		# ##############################
		# Render the road front to back
		# ##############################
		baseSegment:RoadSegment = self.findSegment(self.position) # get current segment according to position
		playerSegment:RoadSegment = self.findSegment(self.position+Road.PLAYERZ)
		baseSegmentIndex = baseSegment.getIndex()
		maxy = HEIGHT # y cannot be greater than Surface height
		horizon = HEIGHT

		playerPercent = self.percentRemaining(self.position+Road.PLAYERZ, Road.SEGMENTLENGTH)
		playery = self.interpolate(playerSegment.p1.world.y, playerSegment.p2.world.y, playerPercent)		
		positioninsegment = (self.position%Road.SEGMENTLENGTH)/Road.SEGMENTLENGTH
		x = 0
		dx = -(baseSegment.curve * positioninsegment) #for the first segment we compute the ratio depending on the position within this segment


		# Background image
		if(baseSegment!=self.lastsegment):
			self.direction -= baseSegment.curve # compute current road direction
			self.lastsegment = baseSegment
		xbackground = WIDTH/2-Road.background.get_width()/2+self.direction
		if(xbackground<0):
			while(abs(xbackground)>Road.background.get_width()):
				xbackground+=Road.background.get_width()
		if(xbackground>0):
			while(xbackground>0):
				xbackground-=Road.background.get_width()
		#self.image.fill(Road.SKYCOLOR) # clear image
		self.image.blit(Road.background, (xbackground, 0)) # draw background with a small scrolling
		if(xbackground+Road.background.get_width()<WIDTH):
			self.image.blit(Road.background, (xbackground+Road.background.get_width(), 0))


		for n in range(len(self.tracksegments)):
			segment:RoadSegment = self.tracksegments[n]
			segment.resetProjection()

		for n in range(Road.DRAWDISTANCE):
			# get current segment to draw
			segmentindex = (baseSegmentIndex + n) % len(self.tracksegments)
			segment:RoadSegment = self.tracksegments[segmentindex]
			segment.setSpriteClip(horizon)
			# do compute the segment screen position according to the current position
			currentposition = self.position-Road.TRACKLENGTH if segmentindex<baseSegmentIndex else  self.position # looping back...
			segment.doProjection((self.playerx * Road.ROADWIDTH)-x, playery + Road.CAMERAHEIGHT, currentposition, Road.CAMERADEPTH, WIDTH, HEIGHT, Road.ROADWIDTH, dx)

			x += dx
			dx +=	segment.curve
			segment.setFog(n/Road.DRAWDISTANCE, Road.FOGDENSITY)

			# skip the segment if it is not visible
			if ((segment.p1.camera.z <= Road.CAMERADEPTH) or 	# behind us
				(segment.p2.screen.y >= segment.p1.screen.y) or # backface
				(segment.p2.screen.y >= maxy)):          		# clip by (already rendered) segment
				continue

			# otherwise render it on the screen
			segment.render(self.image, time, WIDTH)
			
			# update our maxy for clipping
			maxy = segment.p1.screen.y
			# floating horizon for sprite rendering front to back...
			horizon = min(min(horizon, segment.p1.screen.y), segment.p2.screen.y)

		# ###########################################
		# Render the sides and the cars back to front
		# ###########################################

		# render sides
		firstsegments = int(Road.PLAYERZ/Road.SEGMENTLENGTH)+1 # we skip the segments between the camera and the car
		if(Road.CAMERAHEIGHT<1000):
			firstsegments+=1
		for n in range(Road.LAYOUTDRAWDISTANCE, firstsegments, -1):
			# get current segment to draw
			segmentindex = (baseSegmentIndex + n) % len(self.tracksegments)
			segment:RoadSegment = self.tracksegments[segmentindex]

			# skip the segment if it is not visible
			if (segment.p1.camera.z <= Road.CAMERADEPTH):  	# behind us
				continue

			segment.renderSprites(self.image, time, WIDTH)

	def setPosition(self, position):
		self.position = position
		self.position = self.position % Road.TRACKLENGTH

	def forward(self, val):
		val = min(max(0, val), Road.MAXSPEED)
		self.position += val
		self.position = self.position % Road.TRACKLENGTH

	def backward(self, val):
		val = min(max(0, val), Road.MAXSPEED)
		self.position -= val
		if(self.position<0):
			self.position += Road.TRACKLENGTH

	def left(self, val):
		self.playerx -= val
		if(self.playerx<-2):
			self.playerx = -2

	def right(self, val):
		self.playerx += val
		if(self.playerx>5): # 2 + road segment offset
			self.playerx = 5

	def turn(self, val):
		if(val!=0):
			self.playerx += val
			if(self.playerx<-2):
				self.playerx = -2
			elif(self.playerx>5): # 2 + road segment offset
				self.playerx = 5

	def getCentrifugalEffect(self):
		segment:RoadSegment = self.findSegment(self.position)
		curve = segment.curve
		return - curve * Road.CENTRIFUGAL

	def updateCarsPositionOnRoad(self, carslist:list[Cars]):
		'''
		update cars position on the road to prepare for rendering
		'''
		# position the cars in their corresponding road segment for rendering
		for car in carslist:
			segment = self.findSegment(car.z)
			car.setRoadSegment(segment)

	def updateFerrariPositionOnRoad(self, ferrari):
		'''
		update ferrari position on road to prepare for renderinf
		'''
		segment = self.findSegment(self.position)
		ferrari.setRoadSegment(segment)

	def getCarSegment(self):
		return self.findSegment(self.position+Road.PLAYERZ)


	def setCameraHeight(self, height):
		Road.CAMERAHEIGHT = height
		Road.PLAYERZ = int(Road.CAMERAHEIGHT * Road.CAMERADEPTH)


	def	getCarWidth(self, width):
		cameraz     = Road.PLAYERZ
		screenscale = Road.CAMERADEPTH/cameraz
		screenw     = int((screenscale * Road.ROADWIDTH * width/2))
		carw = (screenw)/3
		return carw

	def isOffRoad(self):
		segment = self.getCarSegment()
		if(self.playerx<-1 or self.playerx>segment.getRightBorder()):
			return True
		else:
			return False

	def isCollidingCar(self):
		segment =self.getCarSegment()
		return segment.isCollidingCar(self.playerx)