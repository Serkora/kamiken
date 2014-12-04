#!/usr/bin/env python3


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
	
	def __init__(self, window):
		self.width = window.width
		self.height = window.height
		self.space = []
		self.walls = []
		self.dungeon = ones([self.width, self.height])
		'''
		Ничто не мешает нам инвертировать здесь или в выводе и "рисовать"
		не пустотой, а наоборот "стенками"
		'''
	def shooting(self, bullets):
		#bullets = random.randint(2, 5)
		for i in range(bullets+1):
			x = random.randint(0, self.width-1)
			y = random.randint(0, self.height-1)
			self.dungeon[x, y] = 0
			self.counting() #я считаю координаты нуликов и единичек
			#Здесь они используются только для роста, а в collisions
			#по ним и рисуется (список из двух координат). добавить
			#третью координату- будет трехмерное подземелье
	'''
	Супер функция пригодилась (как я и предполагал) - небольшими изменениями
	в ней можно менять форму роста. Пока просто стираются все смежные еди-
	нички, раскомментив условие (или поменяв его) можно получить наркоманию
	'''
	def growing(self, N):
		for i in range(N):
			for vert in self.space:
				coordinates = self.super_function(vert[0], vert[1])
				for cord in coordinates:
					try:
						self.dungeon[cord[0],cord[1]] = 0
					except:
						pass
		self.counting()
		
	def growing2(self,N):
		for space in self.space:
			coordinates = self.super_function(vert[0], vert[1])
			cord = random.choice(coordinates)

	def counting(self):
		self.space = []
		self.walls = []
		for x in range(self.width-1):
			for y in range(self.height-1):
				
				if self.dungeon[x,y] == 0:
					self.space.append([x,y])
				else:
					self.walls.append([x,y])
	
	def super_function(self, I, J): 
		coordinates = []
		for i in range(I - 1, I + 2):
			for j in range(J - 1, J + 2):
				#print(i , j )
				#if (i - j) % 2 != 0:
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
generator = Generator(win)



'''
g - новое подземелье, заполняет # 
r - стреляем семенами, одно нажатие 10 пулек
c - из семян растут комнаты, одно нажатие - одна итерация
b - предустановка, генерирует такие себе пещерки
q - корректный выход
'''



while True:

	c = win.window.getch()
	if c == ord('g'):
		generator = Generator(win)
		win.draw(generator)
	elif c == ord('q'):
		curses.endwin()
		break
	elif c == ord('c'):
		generator.growing(1)
		win.draw(generator)
	elif c == ord('r'):
		generator.shooting(10)
		win.draw(generator)
	elif c == ord('o'):
		generator.shooting(1)
		
	elif c == ord('b'):
		generator = Generator(win)
		generator.shooting(50)
		generator.growing(5)
		win.draw(generator)
		
	


