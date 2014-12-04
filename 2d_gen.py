import numpy as np
from numpy import ones
import random
import curses


tiles = {			0.0		: '.',
				1.0		: '#',
				2.0		: ' ',
				3.0		: ' ',
				4.0		: ' '		}


class Generator(object):
	
	def __init__(self, window, bullets):
		self.width = window.width
		self.height = window.height
		self.bullets = bullets
		self.dungeon = ones([self.width, self.height])
		self.centers = []
		self.shooting()
		#self.growing()
	def shooting(self):
		#bullets = random.randint(2, 5)
		for i in range(self.bullets+1):
			x = random.randint(0, self.width-1)
			y = random.randint(0, self.height-1)
			self.dungeon[x, y] = 0
			self.centers.append([x, y])
			#print(self.centers)
	
	def growing(self):
		for i in self.centers:
			#square = random.randint(1, self.BRD_W//2)
			square = 2
			for x in range(i[0]-square, 1, i[0]+square):
				for y in range(i[1]-square, 1, i[1]+square):
					if x >= 0 and y >= 0:
						self.dungeon[x, y] = 0
					
	def rect(self):
		#a = random.choice(self.centers)
		#b = random.choice(self.centers)
		space = []
		for x in range(self.width-1):
			for y in range(self.height-1):
				if self.dungeon[x,y] == 0:
					space.append([x, y])
		for vert in space:
			coordinates = self.super_function(vert[0], vert[1])
			for cord in coordinates:
				try:
					self.dungeon[cord[0],cord[1]] = 0
				except:
					pass
		#self.dungeon[a[0]+1, a[1]] = 0
		#if a != b:
			#pass
		#	for x in range(a[0], 1, a[0]+3):
		#		for y in range(a[1], 1, a[1]+3):
		#			self.dungeon[x, y] = 0
	def super_function(self, I, J): 
		coordinates = []
		for i in range(I - 1, I + 2):
			for j in range(J - 1, J + 2):
				#print(i , j )
				#if (i - j) % 2 != 1:
				coordinates.append([i, j])
		return(coordinates)
		
		
class Window(object):
	
	def __init__(self, height, width):
		self.height = height
		self.width = width
		self.screen = curses.initscr()
		curses.noecho()
		self.window = curses.newwin(height, width)
		self.pad = curses.newpad(height, width)
	
	def draw(self, generator):
		for x in range(0, generator.width):
			for y in range(0, generator.height):
				try:
					tile = tiles[generator.dungeon[x, y]] 
					self.pad.addch(x,y, tile)
				except curses.error:
					pass
		self.pad.refresh(0,0, 0,0, self.height, self.width)





win = Window(20, 20)
generator = Generator(win, 10)


while True:

	c = win.window.getch()
	if c == ord('g'):
		generator.growing()
		win.draw(generator)
	elif c == ord('q'):
		curses.endwin()
		break
	elif c == ord('c'):
		win.draw(generator)
	elif c == ord('n'):
		generator = Generator(win, 50)
	elif c == ord('r'):
		generator.rect()
	elif c == ord('b'):
		generator = Generator(win, 50)
		for i in range(1):
			generator.rect()
		win.draw(generator)
	


