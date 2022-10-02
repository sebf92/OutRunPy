import pygame, random, math
from constants import *

class Side():
	WATER = 0
	SAND = 1
	GRANDSTAND = 2

	RATIO = 2

	LEFT = 0
	RIGHT = 1

	tiles = None
	sideimages = None

	sideinfos = [	("water1", 127, 425, 244, 32)
					,("water2", 127, 458, 244, 30)
					,("sand1", 453, 376, 244, 32)
					,("grandstand", 474, 230, 188, 65)
					#,("start", 1, 234, 472, 61)
					#,("goal", 605, 528, 472, 62)
				]

	sequence = [
		('water', True, True, [0]), # name, repeatx, wavemode, images index
		('sand', True, False, [2]),
		('grandstand', False, False, [3])
	]

	imagecache = {}

	globalcounter = 0

	buffer = None

	def __init__(self, type):
		Side.globalcounter += 1

		if(Side.buffer==None):
			Side.buffer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32).convert_alpha()

		if(Side.tiles == None):
			# Load tiles
			Side.tiles = pygame.image.load("./sprites/spriteslvl1.png")
			Side.tiles = Side.tiles.convert_alpha()
			imglist = list()
			for i in range(len(Side.sideinfos)):
				(name,x,y,w,h) = Side.sideinfos[i]
				img = Side.tiles.subsurface(pygame.Rect(x, y, w, h))
				imglist.append(img)
			Side.sideimages = imglist

		self.roadsegment = None
		self.x = 0
		self.y = 0
		self.position = 0
		self.leftright = Side.LEFT
		self.zoomfactor = 1
		type = min(max(0, type), len(Side.sideimages)-1)
		self.type = type
		self.index = random.randint(0,10)
		self.repeatx = Side.sequence[self.type][1]
		self.wavemode = Side.sequence[self.type][2]
		self.waveTime = 0
		self.tileTime = 0
		self.image = None
		self.rect = None

		self.angle = Side.globalcounter*10

	def update(self, time, clipy:int):
		(n, rp,wm,  currentsequence) = Side.sequence[self.type]
		self.index = self.index % len(currentsequence)
		plant = Side.sideimages[currentsequence[self.index]]

		self.waveTime += time
		if(self.waveTime>50):
			self.index += 1
			self.angle += 10
			self.angle = self.angle %360
			self.waveTime = 0

		self.tileTime += time
		if(self.tileTime>200):
			self.index += 1
			self.tileTime = 0

		currentwidth = int(plant.get_width()*Side.RATIO*self.zoomfactor)
		currentheight = int(plant.get_height()*Side.RATIO*self.zoomfactor)

		if(currentheight<3):
			scaledplant = None # skip drawing...
			return


		if(self.leftright == Side.LEFT): 	#LEFT side
			x = self.x-currentwidth
		else: 				#RIGHT side
			x = self.x

		if(self.wavemode == True):
			x = x+math.sin(self.angle*2*math.pi/360)*20*self.zoomfactor

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
			key = n+'.'+str(currentwidth)+'.'+str(currentheight)
			if(key in Side.imagecache):
				scaledplant = Side.imagecache[key]
			else:
				#scaledplant = Side.buffer.subsurface(0, 0, currentwidth, currentheight) # scale the sprite
				#scaledplant.fill((0,0,0,0))
				scaledplant = pygame.transform.scale(plant, (currentwidth, currentheight)) 
				scaledplant.set_alpha( 255 )
				Side.imagecache[key] = scaledplant
			if(clippedheight>0): #take only a subportion of the sprite... if needed
				scaledplant = scaledplant.subsurface(0, 0, currentwidth, clippedheight)
		else:
			scaledplant = None # skip drawing...
			return

		# flip image if needed
		if(self.leftright == Side.RIGHT and scaledplant!=None):
			scaledplant = pygame.transform.flip(scaledplant, True, False)

		self.image = scaledplant
		self.rect = pygame.Rect(x, y, currentwidth, clippedheight)

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setZoomFactor(self, zoomfactor):
		self.zoomfactor = zoomfactor

	def setLeftRight(self, s):
		self.leftright = s

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
		if not self.repeatx:
			return None
		else:
			return self.leftright
