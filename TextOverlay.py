import pygame

class TextOverlay(pygame.sprite.Sprite):

	# Constructeur de la classe
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.rect = pygame.Rect(0,0,1,1)
		self.deltaTime = 0
		self.font = pygame.font.Font("./font/FreeSansBold.ttf", 24)
		self.text = None

		self.setText('Text Overlay')
		self.setColor((255,255,255,255))
		self.setSize(36)


	def update(self,time):
		if(self.dirty):
			self.updateImage()
	
	def setPosition(self, x, y):
		self.rect = pygame.Rect(x,y,self.rect.width,self.rect.height)

	# Position courante du sprite pour les tests de collision
	def getPosition(self):
		return self.rect

	def setText(self, text):
		if(self.text != text):
			self.text = text
			self.dirty = True

	def setSize(self, size):
		self.size = size
		self.font = pygame.font.Font("./font/FreeSansBold.ttf", size)
		self.dirty = True

	def setColor(self, color):
		self.color = color
		self.dirty = True

	def updateImage(self):
		self.image = self.font.render(self.text, True, self.color)
		self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())
		self.dirty = False

