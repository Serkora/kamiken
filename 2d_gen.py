#!/usr/bin/env python3


import numpy as np
from numpy import ones, eye, zeros
import random
import curses


tiles = {			0.0		: '.',
				1.0		: '#',
				2.0		: '/',
				3.0		: ' ',
				4.0		: ' '		}


class Generator(object):
	
	def __init__(self, height, width):
		self.width = width
		self.height = height
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
			
	def clearing(self, x, y):
		if 0<=x<=self.width-1 and 0<=y<=self.height-1:
			self.dungeon[x,y] = 0
		else:
			pass
	'''
	Рост из пустых клеток: все смежные с каждой пустой клеткой стираются.
	При малом N комнатки получаются правильной формы, при достаточном
	для соединения нескольких комнат в одну - самой разнообразной
	'''
	def growing(self, N):
		for i in range(N):
			for vert in self.space:
				coordinates = self.super_function(vert[0], vert[1])
				for cord in coordinates:
					self.clearing(cord[0],cord[1])
		self.counting()
	'''
	Случайным образом выбирается одна клетка из смежных с пустой. Все 
	смежные с ней клетки очищаются. Повторяется для всех пустых клеток,
	имеющихся в self.space на момент вызова функции.
	'''
	def growing2(self):
		for vert in self.space:
			coordinates = self.super_function(vert[0], vert[1])
			cord = random.choice(coordinates)
			new_coordinates = self.super_function(cord[0],cord[1])
			for cord in new_coordinates:
				self.clearing(cord[0],cord[1])
		self.counting()
		
		
	def growing3(self, N):
		for i in range(N):
			for vert in self.space:
				self.space.remove(vert)
				coordinates = self.super_function(vert[0], vert[1], True)
				cord = random.choice(coordinates)
				self.clearing(cord[0],cord[1])
			self.counting()
			
	
	def space_counting(self):
		rooms = []
		n = 0
		for i in range(len(self.space)):
			for j in range(len(self.space)):
				if self.adjacency_matrix[i,j] == 1:
					rooms[n].append(self.cord_to_ind[i],self.cord_to_ind[j])
					
	
	
	def adjacency(self):
		self.cord_to_ind = {}.fromkeys(range(len(self.space)))  
		for key in self.cord_to_ind:
			self.cord_to_ind[key] = self.space[key]
		#print(self.cord_to_ind)
		self.adjacency_matrix = zeros([len(self.space),len(self.space)])
		for i in range(len(self.space)):
			for j in range(len(self.space)):
				vert = self.cord_to_ind[i]
				coordinates = self.super_function(vert[0], vert[1], True)
				if self.cord_to_ind[j] in coordinates:
					self.adjacency_matrix[i,j] = 1
		#print(self.adjacency_matrix)
	
	#def connection(self):
		
	
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
	'''
	По дефолту флаг ложь - проверяет все смежные клетки (по горизонталям,
	вертикалям и диагоналям). Флаг истина - проверяет ссоседние клетки (по 
	горизонталям и вертикалям)
	'''
	def super_function(self, I, J, flag=False): 
		coordinates = []
		for i in range(-1, +2):
			for j in range(-1, +2):
				if flag:
				#print(i , j )
					if abs(i - j) % 2 == 1:
						coordinates.append([I+i,J+j])
						#print('True')
				else:
					coordinates.append([I+i,J+j])
		return(coordinates)
		
		
class Window(object):
	
	def __init__(self, height, width):
		self.height = height
		self.width = width
		self.screen = curses.initscr()
		curses.noecho()
		#self.window = curses.newwin(20, 20)
		self.pad = curses.newpad(height, width)
	
	def draw(self, generator):
		for x in range(0, generator.width):
			for y in range(0, generator.height):
				try:
					tile = tiles[generator.dungeon[x, y]] 
					self.pad.addch(x,y, tile)
				except curses.error:
					pass
		self.pad.refresh(0,0, 0,0, 20, 75)




height, width = 24, 24
win = Window(height, width)
generator = Generator(height, width)



'''
g - новое подземелье, заполняет # 
r - стреляем семенами, одно нажатие 10 пулек
c - из семян растут комнаты, одно нажатие - одна итерация
o - копаем более хитрым образом: стреляет в массив один раз, затем расширяет дырку 
на одну клетку, затем выбирает случайно одну из клеток стены, копает вокруг нее,
снова выбирает случайную клетку стены... Все равно не обязательно замкнуто, потому
что если пещера касается края матрицы, то копаие происходит на противоположной стенке.
v - рост третим способом
d - нинужная пока функция которая ничего полезного не делает. кроме того, что
позволяет обойтись без обязательно связных областей - она заменяет некоторые тайлы стены
на "дверь". Можно попросту удалять стену в этом месте, и тогда области точно станут 
замкнутыми (если между ними один тайл, разумеется)
b - предустановка, генерирует такие себе пещерки (не обязательно связные. но часто)
q - корректный выход
'''



while True:

	c = win.screen.getch()
	if c == ord('g'):
		generator = Generator(height, width)
		win.draw(generator)
	elif c == ord('q'):
		curses.endwin()
		break
	elif c == ord('c'):
		generator.growing(1)
		win.draw(generator)
	elif c == ord('r'):
		generator.shooting(0)
		win.draw(generator)
	elif c == ord('v'):
		generator.growing3(10)
		win.draw(generator)
	elif c == ord('o'):
		generator.shooting(0)
		generator.growing(1)
		generator.growing2()
		win.draw(generator)
	elif c == ord('d'):
		generator.doors()
		win.draw(generator)
	elif c == ord('a'):
		generator.adjacency()
	elif c == ord('b'):
		generator = Generator(height, width)
		generator.shooting(50)
		generator.growing(5)
		win.draw(generator)
		
	


