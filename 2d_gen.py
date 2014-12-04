#!/usr/bin/env python3


import numpy as np
from numpy import ones
import random
import curses


tiles = {			0.0		: '.',
				1.0		: '#',
				2.0		: '/',
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
		
	def growing2(self):
		for vert in self.space:
			coordinates = self.super_function(vert[0], vert[1])
			cord = random.choice(coordinates)
			new_coordinates = self.super_function(cord[0],cord[1])
			for cord in new_coordinates:
				try:
					self.dungeon[cord[0],cord[1]] = 0
				except:
					pass
		self.counting()
			

	def counting(self):
		self.space = []
		self.walls = []
		for x in range(self.width-1):
			for y in range(self.height-1):
				
				if self.dungeon[x,y] == 0:
					self.space.append([x,y])
				else:
					self.walls.append([x,y])
					
	def doors(self):
		'''
		Что то не так все таки. Как то он двери неправильно ставит -
		вроде сказал ему, ставь только если ровно два соседних по 
		вертикали или горизонтали тайла - пустые. А он часто рисует 
		зачем то соседние с угловыми.
		'''
		for x in range(self.width-1):
			for y in range(self.height-1):
				coordinates = self.super_function(x, y, True)
				
				count = 0
				count_w = 0
				if self.dungeon[x,y] == 1:
					for cord in coordinates:
						if self.dungeon[cord[0],cord[1]] == 0:
							count+=1
						#elif self.dungeon[cord[0],cord[1]] == 1:
						#	count_w+=1
					if count == 2: #and count_w>=2:
						self.dungeon[x,y] = 2
	
	def super_function(self, I, J, flag=False): 
		coordinates = []
		for i in range(I - 1, I + 2):
			for j in range(J - 1, J + 2):
				if flag:
				#print(i , j )
					if abs(i - j) % 2 != 1:
						coordinates.append([i, j])
						#print('True')
				else:
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
o - копаем более хитрым образом: стреляет в массив один раз, затем расширяет дырку 
на одну клетку, затем выбирает случайно одну из клеток стены, копает вокруг нее,
снова выбирает случайную клетку стены... Все равно не обязательно замкнуто, потому
что если пещера касается края матрицы, то копаие происходит на противоположной стенке.
d - нинужная пока функция которая ничего полезного не делает. кроме того, что
позволяет обойтись без обязательно связных областей - она заменяет некоторые тайлы стены
на "дверь". Можно попросту удалять стену в этом месте, и тогда области точно станут 
замкнутыми (если между ними один тайл, разумеется)
b - предустановка, генерирует такие себе пещерки (не обязательно связные. но часто)
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
		generator.shooting(0)
		generator.growing(1)
		generator.growing2()
		win.draw(generator)
	elif c == ord('d'):
		generator.doors()
		win.draw(generator)
	elif c == ord('b'):
		generator = Generator(win)
		generator.shooting(50)
		generator.growing(5)
		win.draw(generator)
		
	


