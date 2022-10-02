# ###############################################################################
#
# A car simulation game from the 80's...
#
#
#
# ###############################################################################

import pygame, sys, gc

from constants import *
from road import *
from Ferrari import *
from FerrariDust import *
from Cars import *
from SpeedGauge import *
from SoundSystem import *
from MusicScreen import *
from SplashScreen import *
from ScoreScreen import *
from TextOverlay import TextOverlay

def main(args:list[str]) -> int:
	pygame.init()
	pygame.joystick.init()
	joystick_count = pygame.joystick.get_count()
	if(joystick_count>0):
		joystick = pygame.joystick.Joystick(0)
		joystick.init()
	else:
		joystick = None
	pygame.mouse.set_visible(False)
	pygame.display.set_caption(TITLE)
	gc.disable()

	if(FULLSCREEN):
		screen:pygame.Surface = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1)
	else:
		screen:pygame.Surface = pygame.display.set_mode((WIDTH,HEIGHT))

	soundsystem = SoundSystem()

	splashScreen = SplashScreen(soundsystem)
	splashScreen.run(screen)

	musicScreen = MusicScreen(soundsystem)
	musicScreen.run(screen)

	road = Road()

	ferrari = Ferrari()
	ferrari.setXY(WIDTH/2, HEIGHT-10)
	ferrari.setSlope(Ferrari.SLOPE_MIDDLE)
	ferrari.setDirection(Ferrari.DIRECTION_STRAIGHT)

	smokeEffect = FerrariDust(FerrariDust.SMOKE)
	smokeEffect.setXY(WIDTH/2, HEIGHT-10)

	dustEffect = FerrariDust(FerrariDust.DUST)
	dustEffect.setXY(WIDTH/2, HEIGHT-10)

	cars:list[Cars] = list()
	for i in range(5000*3, road.TRACKLENGTH, 5000):
		car = Cars(road.TRACKLENGTH, random.randint(0,5))
		car.setZ(i)
		car.setPosition(random.randint(-8,8)/10)
		car.setTrack(random.randint(0,1))
		car.setSpeed(150)
		cars.append(car)

	speedgauge = SpeedGauge()
	speedgauge.setXY(10,10)

	fpswidget = TextOverlay()
	fpswidget.setPosition(10, HEIGHT-30)
	fpswidget.setSize(24)
	fpswidget.setText('00 FPS')

	showfps = False
	direction = 0
	speed = 0
	carspeed = 0
	clock = pygame.time.Clock()
	next = False
	ferrariSizeInitialized = False
	while not next:
		# limit display at FPS (img/sec)
		elapsedtime = clock.tick(FPS)	
		
		# compute current FPS
		nbimagessec = 1000//elapsedtime
		nbimagessec = max(1, nbimagessec)

		txtnbimagessec = str(nbimagessec) + " FPS"
		fpswidget.setText(txtnbimagessec)

		# manage keyboard events
		###################
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				pygame.quit()
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_1:
					soundsystem.playMusic(soundsystem.MAGICAL_SOUND_SHOWER)
				elif event.key == pygame.K_2:
					soundsystem.playMusic(soundsystem.PASSING_BREEZE)
				elif event.key == pygame.K_3:
					soundsystem.playMusic(soundsystem.SPLASH_WAVE)
				elif event.key == pygame.K_4:
					soundsystem.playMusic(soundsystem.TESTAROSSA_AUTODRIVE)
				elif event.key == pygame.K_KP1:
					road.setCameraHeight(600)
					ferrariSizeInitialized = False
				elif event.key == pygame.K_KP2:
					road.setCameraHeight(1000)
					ferrariSizeInitialized = False
				elif event.key == pygame.K_KP3:
					road.setCameraHeight(2000)
					ferrariSizeInitialized = False
				elif event.key == pygame.K_UP:
					ferrari.setAcceleration(True)
				elif event.key == pygame.K_DOWN:
					ferrari.setBreaking(True)
				elif event.key == pygame.K_LEFT:
					direction = -1
				elif event.key == pygame.K_RIGHT:
					direction = 1
				elif event.key == pygame.K_SPACE:
					next = True
				elif event.key == pygame.K_f:
					showfps = not showfps
				elif event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit(0)
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					direction = 0
				elif event.key == pygame.K_RIGHT:
					direction = 0
				elif event.key == pygame.K_UP:
					ferrari.setAcceleration(False)
				elif event.key == pygame.K_DOWN:
					ferrari.setBreaking(False)

		if(road.isCollidingCar()):
			ferrari.accident()

		ferrari.offroad(road.isOffRoad())

		speed = ferrari.getSpeed()
		speedPercent  = speed/Road.MAXSPEED
		dx            = 3 * speedPercent / nbimagessec # at top speed, should be able to cross from left to right (-1 to 1) in 1 second
		# add centrifugal effect if needed
		speed2Percent  = (speed*speed)/(Road.MAXSPEED*Road.MAXSPEED)
		centrifugalx = road.getCentrifugalEffect()*speed2Percent
		road.turn(centrifugalx)


		if(direction == -1): # turn the wheel
			ferrari.setDirection(Ferrari.DIRECTION_LEFT2)
			road.left(dx)
		elif(direction == 1):
			ferrari.setDirection(Ferrari.DIRECTION_RIGHT2)
			road.right(dx)
		else:
			if(centrifugalx<0): # small turn if we have a curve and the player does not turn the wheel...
				ferrari.setDirection(Ferrari.DIRECTION_RIGHT1)
			elif(centrifugalx>0):
				ferrari.setDirection(Ferrari.DIRECTION_LEFT1)
			else:
				ferrari.setDirection(Ferrari.DIRECTION_STRAIGHT)

		if(showfps):
			fpswidget.update(elapsedtime)

		# update Ferrari speed gauge and move forward
		speedgauge.setSpeed(speed)
		road.forward(int(speed*60/nbimagessec))

		# let's make the cars moving and update their position on the road
		if(carspeed<130):
			carspeed = speed
		else:
			carspeed = 130
		for car in cars:
			car.setSpeed(carspeed) # slowly accelerate at the beginning of the game...
			car.move()
		road.updateCarsPositionOnRoad(cars)
		road.updateFerrariPositionOnRoad(ferrari)

		road.update(elapsedtime) # displays both the road and its content (sides, cars)
		speedgauge.update(elapsedtime) # overlay
		ferrari.update(elapsedtime) # Player Ferrari
		smokeEffect.update(elapsedtime) # Ferrari effect
		dustEffect.update(elapsedtime) # Ferrari effect

		# reinit the ferrari size every time we change the camera height
		# as the car size is computed based on the road size
		if(not ferrariSizeInitialized):
			ferrariSizeInitialized = True
			ferrari.setCarWidth(road.getCarWidth(WIDTH))
			smokeEffect.setCarWidth(road.getCarWidth(WIDTH))
			dustEffect.setCarWidth(road.getCarWidth(WIDTH))

		# update screen buffer
		screen.blit(road.image, road.rect)
		screen.blit(speedgauge.image, speedgauge.rect)
		screen.blit(ferrari.image, ferrari.rect)

		if(ferrari.isAccidented()):
			if(road.isOffRoad() and ferrari.getSpeed()>0):
				screen.blit(dustEffect.image, dustEffect.rect)
			elif(not road.isOffRoad() and ferrari.getSpeed()>0):
				screen.blit(smokeEffect.image, smokeEffect.rect)
		else:
			if(not road.isOffRoad()):
				if(ferrari.getSpeed()>0 and ferrari.getSpeed()<50 and ferrari.getAcceleration()==True):
					screen.blit(smokeEffect.image, smokeEffect.rect)
				if(abs(centrifugalx)>0.03):
					screen.blit(smokeEffect.image, smokeEffect.rect)
			else:
				if(road.isOffRoad() and ferrari.getSpeed()>0):
					screen.blit(dustEffect.image, dustEffect.rect)


		if(showfps==True):
			screen.blit(fpswidget.image, fpswidget.rect)

		# flip screen (update screen with double buffering)
		pygame.display.update()
	
	scoreScreen = ScoreScreen(soundsystem)
	scoreScreen.run(screen)

	pygame.quit()
	return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))