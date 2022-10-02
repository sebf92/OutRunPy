# ####################################
# A road segment
#
# ####################################

from typing import Tuple
import pygame, math

from pygame.sprite import Sprite
from Cars import Cars

class Point3D():
	x = 0
	y = 0
	z = 0

class PointScreen():
	x = 0
	y = 0
	w = 0
	scale = 0

class PointRoad():
	def __init__(self):
		self.world = Point3D() # original coordinate in the 3D world (static values)
		self.camera = Point3D() # translated world coordinate according to the camera position (transient values, used during rendering)
		self.screen = PointScreen() # screen coordinate with the width of the road according to its z distance (transient values, used during rendering)

class RoadSegment():
	SEGMENTLENGTH  = 200  			# length of a single segment

	LIGHT = 0
	DARK = 1

	'''
	A road segment
	'''
	def __init__(self, index, worldy1, worldz1, worldy2, worldz2, curve, color, segmentlength, lanes):
		'''
		Init a road segment giving an index, 2 z coordinates and a color
		'''
		self.index = index
		RoadSegment.SEGMENTLENGTH = segmentlength

		self.previoussegment:RoadSegment = None
		self.nextsegment:RoadSegment = None

		self.p1 = PointRoad()
		self.p1.world.y = worldy1
		self.p1.world.z = worldz1

		self.p2 = PointRoad()
		self.p2.world.y = worldy2
		self.p2.world.z = worldz2

		self.lanes = lanes
		self.curve = curve
		self.gap = 3 #gap between the both road (in roadwidth/2)

		self.clip = 0 # used to clip the sprites
		self.currentCameraZ = 0

		self.cars:list[Cars] = list() # contains a series of (cars)
		self.sprites:Tuple(int, Sprite) = list() # contains a series of (xoffset, Sprite)
		self.spritezoomfactor = 1 # sprite zoom ratio computed during 'transform'

		# init colors depending on the theme
		self.fog = 1
		self.color = color
		self.ROADCOLOR = None
		self.SANDCOLOR = None
		self.GRASSCOLOR = None
		self.RUMBLECOLOR = None
		self.LANECOLOR = None
		self.LFOGCOLOR = pygame.Color("#E8D5C0")
		self.RFOGCOLOR = pygame.Color("#E8D5C0")
		if(self.color == RoadSegment.LIGHT):
			self.ROADCOLOR = pygame.Color("#6B6B6B")
			self.GRASSCOLOR = pygame.Color("#10AA10")
			self.SANDCOLOR = pygame.Color("#EEDDCA")
			self.SEACOLOR = pygame.Color("#8ECCFF")
			self.RUMBLECOLOR = pygame.Color("#555555")
			self.ORUMBLECOLOR = pygame.Color("#BBBBBB")
			self.LANECOLOR = pygame.Color("#CCCCCC")
		else:
			self.ROADCOLOR = pygame.Color("#696969")
			self.GRASSCOLOR = pygame.Color("#009A00")
			self.SANDCOLOR = pygame.Color("#E8D5C0")
			self.SEACOLOR = pygame.Color("#78C1FF")
			self.RUMBLECOLOR = pygame.Color("#BBBBBB")
			self.ORUMBLECOLOR = pygame.Color("#555555")
			self.LANECOLOR = pygame.Color("#696969")

	def getIndex(self):
		'''
		returns the road segment index
		'''
		return self.index

	def resetProjection(self):
		self.spritezoomfactor = 0

	def doProjection(self, cameraX, cameraY, cameraZ, cameraDepth, width, height, roadWidth, curve):
		'''
		Compute translated coordinates and screen coordinates
		'''
		self.currentCameraZ = cameraZ
		# step 1 : compute road segment screen coordinates
		if(self.previoussegment==None): # if the segment is linked, p1 is actually shared with the previous segment and computed by the previous segment, no need to recompute it
			self.projectPoint(self.p1, cameraX-curve, cameraY, cameraZ, cameraDepth, width, height, roadWidth)
		self.projectPoint(self.p2, cameraX-curve, cameraY, cameraZ, cameraDepth, width, height, roadWidth)
		self.spritezoomfactor = 2*self.p1.screen.w/roadWidth

		# step 2 : for each car in the road segment, compute its screen coordinates
		for car in self.cars:
			# compute car direction based on both curve and camera shift
			direction = Cars.RIGHT
			if(self.curve<0):
				direction = Cars.LEFT
			elif(self.curve>0):
				direction = Cars.RIGHT
			else:
				if(cameraX<0):
					direction = Cars.LEFT
				else:
					direction = Cars.RIGHT
			# compute car x,y coordinates
			car.doProjection(direction)

		# step 3 : for each sprite in the side of the road segment, compute its screen coordinates
		for (offset, sprite) in self.sprites:
			sprite.doProjection()

	def projectPoint(self, p : PointRoad, cameraX, cameraY, cameraZ, cameraDepth, width, height, roadWidth):
		'''
		Internal function to compute translated coordinates and screen coordinates
		'''
		p.camera.x     = (p.world.x) - cameraX
		p.camera.y     = (p.world.y) - cameraY
		p.camera.z     = (p.world.z) - cameraZ
		if(p.camera.z==0): # avoid divide by 0
			p.camera.z = 0.00001
		p.screen.scale = cameraDepth/p.camera.z
		p.screen.x     = int((width/2)  + (p.screen.scale * p.camera.x  * width/2))
		p.screen.y     = int((height/2) - (p.screen.scale * p.camera.y  * height/2))
		p.screen.w     = int(             (p.screen.scale * roadWidth   * width/2))

	def rumbleWidth(self, projectedRoadWidth:int, lanes:int) -> int:
		'''
		get rumble width
		'''
		return projectedRoadWidth/max(6, 2*lanes)

	def laneMarkerWidth(self, projectedRoadWidth:int, lanes:int) -> int:
		'''
		get lane marker width
		'''
		return projectedRoadWidth/max(32, 8*lanes)

	def renderSprites(self, surface:pygame.Surface, time, width:int):
		'''
		Render the sprites on the sides
		'''
		if (self.fog < 1.0): # some alpha blending for far away sprites...
			globalAlpha = max(min(256-int((1.0-self.fog)*256),255),0)

		for (offset, sprite) in self.sprites:
			# draw sprites
			sprite.update(time, self.clip)
			if(sprite.image!=None):
				if (self.fog < 1.0): # some alpha blending for far away sprites...
					sprite.image.set_alpha( globalAlpha )
				surface.blit(sprite.image, sprite.rect)
				if(sprite.isRepeating() == 0): # LEFT
					r = pygame.Rect(sprite.rect.x, sprite.rect.y, sprite.rect.w, sprite.rect.h)
					while(r.x+r.w>0):
						d = max(r.w - r.w/5, 1)
						r.x -= d
						surface.blit(sprite.image, r)
				elif(sprite.isRepeating() == 1): # RIGHT
					r = pygame.Rect(sprite.rect.x, sprite.rect.y, sprite.rect.w, sprite.rect.h)
					while(r.x<width):
						d = max(r.w - r.w/5, 1)
						r.x += d
						surface.blit(sprite.image, r)

		for car in self.cars:
			# draw cars
			car.update(self.clip)
			if(car.image!=None):
				if (self.fog < 1.0): # some alpha blending for far away sprites...
					car.image.set_alpha( globalAlpha )
				surface.blit(car.image, car.rect)

	def render(self, surface:pygame.Surface, time, width:int):
		'''
		Render the roadsegment on the provided surface
		'''
		self.renderGrass(surface, time, width)

		self.renderRoad(surface, time, width, 0, 0)
		if(self.gap!=0 or self.previoussegment.gap!=0):
			self.renderRoad(surface, time, width, self.gap, self.previoussegment.gap) #do not render second road if the roads overlap at 100%

		self.renderFog(surface, width)

	def renderGrass(self, surface:pygame.Surface, time, width:int):
		x1 = self.p1.screen.x
		y1 = self.p1.screen.y
		w1 = self.p1.screen.w
		x2 = self.p2.screen.x
		y2 = self.p2.screen.y
		w2  =self.p2.screen.w

		# draw grass
		fillcolor = self.SANDCOLOR
		points = [(0, y1), (x1-w1, y1), (x2-w2, y2), (0, y2)] # left border
		pygame.draw.polygon(surface, fillcolor, points)
		fillcolor = self.SANDCOLOR
		points = [(x1+w1, y1), (width, y1), (width, y2), (x2+w2, y2)] # right border
		pygame.draw.polygon(surface, fillcolor, points)


	def renderRoad(self, surface:pygame.Surface, time, width:int, gap:int, previousgap:int):
		'''
		Render the roadsegment on the provided surface
		'''

		x1 = self.p1.screen.x
		y1 = self.p1.screen.y
		w1 = self.p1.screen.w
		x2 = self.p2.screen.x
		y2 = self.p2.screen.y
		w2  =self.p2.screen.w

		r1 = self.rumbleWidth(w1, self.lanes)
		r2 = self.rumbleWidth(w2, self.lanes)
		l1 = self.laneMarkerWidth(w1, self.lanes)
		l2 = self.laneMarkerWidth(w2, self.lanes)

		x1 = x1 + w1*previousgap # shift the road if needed
		x2 = x2 + w2*gap

		# draw rumbles
		fillcolor = self.RUMBLECOLOR
		if(gap==0 or gap>2):
			points = [(x1-w1-r1, y1), (x1-w1, y1), (x2-w2, y2), (x2-w2-r2, y2)] # left rumble
			pygame.draw.polygon(surface, fillcolor, points)
		points = [(x1+w1+r1, y1), (x1+w1, y1), (x2+w2, y2), (x2+w2+r2, y2)] # right rumble
		pygame.draw.polygon(surface, fillcolor, points)

		# draw road
		fillcolor = self.ROADCOLOR
		points = [(x1-w1, y1), (x1+w1, y1), (x2+w2, y2), (x2-w2, y2)]
		pygame.draw.polygon(surface, fillcolor, points)

		# draw a lane on the middle of the road if we are on a "light" segment
		if(self.color == RoadSegment.LIGHT):
			lanew1 = w1*2/self.lanes
			lanew2 = w2*2/self.lanes
			lanex1 = x1 - w1 + lanew1
			lanex2 = x2 - w2 + lanew2
			fillcolor = self.LANECOLOR
			for lane in range(1, self.lanes):
				points = [(lanex1 - l1/2, y1), (lanex1 + l1/2, y1), (lanex2 + l2/2, y2), (lanex2 - l2/2, y2)]
				pygame.draw.polygon(surface, fillcolor, points)
				lanex1 += lanew1
				lanex2 += lanew2

			# draw additional rumbles
			fillcolor = self.ORUMBLECOLOR
			if(gap==0 or gap>2):
				points = [(x1-w1, y1), (x1-w1+l1, y1), (x2-w2+l2, y2), (x2-w2, y2)] # left rumble
				pygame.draw.polygon(surface, fillcolor, points)
			points = [(x1+w1, y1), (x1+w1-l1, y1), (x2+w2-l2, y2), (x2+w2, y2)] # right rumble
			pygame.draw.polygon(surface, fillcolor, points)
    
	def renderFog(self, surface:pygame.Surface, width):
		if (self.fog < 1):
			y1 = self.p1.screen.y
			w1 = self.p1.screen.w
			x2 = self.p2.screen.x
			y2 = self.p2.screen.y
			w2  =self.p2.screen.w

			self.doRenderFog(surface,0 ,y2 ,x2-w2, y1-y2+1, self.LFOGCOLOR) # left side
			self.doRenderFog(surface,x2-w2 ,y2 ,width, y1-y2+1, self.RFOGCOLOR) # road + right side

	def doRenderFog(self, surface:pygame.Surface, x, y, width, height, color):
		'''
		render fog
		uses a tricky method as pygame drawrect does not support alpha channel
		'''
		if(width<=0 or height<=0):
			return
		s = pygame.Surface((width,height), pygame.SRCALPHA, 32).convert_alpha()
		globalAlpha = int((1.0-self.fog)*256)
		s.set_alpha(globalAlpha)
		s.fill(color)
		surface.blit(s, (x,y))

	def setFog(self, ratio, fogDensity):
		'''
		set fog value
		'''
		self.fog = self.exponentialFog(ratio, fogDensity)

	def exponentialFog(self, ratio, density):
		'''
		ratio: between 0 and 1, the greater the more fog
		'''
		return 1 / math.pow(math.e, (ratio * ratio * density))

	def setNext(self, next):
		self.nextsegment = next

	def setPrevious(self, previous):
		self.previoussegment = previous
		self.p1 = self.previoussegment.p2 # segments are linked, thus p1 is actually the same as previous segment p2

	def next(self):
		return self.nextsegment

	def previous(self):
		return self.previoussegment

	def setSpriteClip(self, clip):
		self.clip = clip

	def getSpriteClip(self):
		return self.clip

	def addSprite(self, position, sprite):
		'''
		position is a round number
		left side ..., -2, -1, ROAD, 1, 2, ..., right side
		'''
		self.sprites.append((position, sprite))

	def addCar(self, car:Cars):
		self.cars.append(car)

	def clearCars(self):
		self.cars.clear()

	def removeCar(self, car:Cars):
		self.cars.remove(car)

	def getRightBorder(self):
		'''
		1 if no double road
		>1 otherwise
		'''
		return self.gap+1

	def isCollidingCar(self, xpos):
		colliding = False
		for car in self.cars:
			if(car.isColliding(xpos)):
				colliding = True
				break
		
		return colliding