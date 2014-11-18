# -*- coding: UTF-8 -*-
'''
Kamiken tiles v0.0.9
To do:
ИСПРАВЛЕНО - после ход полупрозрачный камень рисуется поверх уже поставленного



'''

import pyglet
import numpy as np
import random
import time
import string
from pyglet.window import mouse 
from pyglet.window import key


'''
С цветами в pyglet бида. Фоновый цвет хороши работает только если значение
голубого (третье число) 0 или 255, в противном случае рисует белым. Однако,
если использовать дробные значение (0-125 / 255 = 0.х), то все работает. ОДНАКО,
это распространяется на ФОН (pyglet.gl.glClearColor(*colors['board']) -т.е.
когда работаем непосредственно через OpenGL), а вот цвет label'а, например,
требует параметры в int. ЧСХ label нормально работает с любыми цветами, если
значения RGB целочисленные. И еще- в label так же работает и прозрачность (4-ое
число, альфа-канал), в то время как в фоне он ничего не делает. Т.о. цвет фона
окна нужно указывать с осторожностью и не путать переменные.
'''
colors = {   'white'  : (255, 255, 255, 0.3),
			 'red'	: (255, 0, 0, 0.3),
			 'blue'   : (0, 0, 255, 0.3),
			 'board'  : (0.59, 0.54, 0.51, 0.3),
			 'r_stone': (243, 104, 18, 255),
			 'b_stone': (14, 193, 225, 255)	  }

'''
Переменные 
'''
BOARD_W = 5
BOARD_H = BOARD_W
MSG = 'KAMI~!!'
TILE_SIZE = 30 
FONT = 'Comic Sans MS'
WINDOW_W = BOARD_W * TILE_SIZE + 2 * TILE_SIZE
WINDOW_H = BOARD_H * TILE_SIZE + 2 * TILE_SIZE
BOARD_OPACITY = 40 #opacity 0-255
FADE_STONE_OPACITY = 150
PLAYER = 2.0 #1.0 - red, 2.0 - blue

'''
Изображения
'''
image   = pyglet.resource.image( 'pics/image5.png'	)
r_stone = pyglet.resource.image( 'pics/r_stone.png'   )
b_stone = pyglet.resource.image( 'pics/b_stone.png'   )
r_point = pyglet.resource.image( 'pics/r_point_2.png' )
b_point = pyglet.resource.image( 'pics/b_point_2.png' )
board   = pyglet.resource.image( 'pics/board_5.png'   )
r_board = pyglet.resource.image( 'pics/board_r.png'   )
b_board = pyglet.resource.image( 'pics/board_b.png'   )

tiles = {	0.0		: board,
			 1.0		: r_stone,
			 2.0		: b_stone,
			 3.0		: r_board,
			 4.0		: b_board				}
			 
tilenames = {0.0		: 'board',
			 1.0		: 'r_stone',
			 2.0		: 'b_stone',			   	# Для вывода в консоль состояния 
			 3.0		: 'r_point',   				# клетки при клике.
			 4.0		: 'b_point', 
			 5.0		: 'both'			   }
			
opacity = {  0.0		: BOARD_OPACITY,
			 1.0		: '255',
			 2.0		: '255',
			 3.0		: BOARD_OPACITY*3,
			 4.0		: BOARD_OPACITY*3				}
player_name = { 1.0 : 'Red one',
				2.0 : 'Blue one'  }

'''
Поле
'''
ALL_STONES = np.zeros([BOARD_W, BOARD_H])
#ALL_STONES = np.eye(BOARD_W)
#print(ALL_STONES)

class Board(pyglet.window.Window):

	def __init__(self, WINDOW_W, WINDOW_H, BOARD_W, BOARD_H,
				 MSG, TILE_SIZE, FONT, ALL_STONES, PLAYER			 ):
		super(Board, self).__init__(width=WINDOW_W, height=WINDOW_H,
									caption='Kamiken')
		self.batch = pyglet.graphics.Batch()
		self.batch_fade = pyglet.graphics.Batch()
		self.turn = PLAYER
		self.label = pyglet.text.Label(text=MSG, font_size=TILE_SIZE-10,
									   anchor_x = 'center',
									   font_name=FONT,
									   color=colors['b_stone'],
									   x = self.width//2,
									   y = BOARD_H*TILE_SIZE+TILE_SIZE+5,
									   batch = self.batch
									   )
		self.fps_display = pyglet.clock.ClockDisplay()
		self.FADE_X = 0
		self.FADE_Y = 0
		self.FADE_FLAG = False
 
	def on_draw(self):
		pyglet.gl.glClearColor(*colors['white'])
		self.clear()
		IMG_IN_WINDOW_W = self.width//image.width
		IMG_IN_WINDOW_H = self.height//image.height
		if IMG_IN_WINDOW_W == 0:
			IMG_IN_WINDOW_W += 1
		if IMG_IN_WINDOW_H == 0:
			IMG_IN_WINDOW_H += 1
		for i in range(IMG_IN_WINDOW_W*4-1):
			for j in range(IMG_IN_WINDOW_H*4-1):
				image.blit(x=i*image.width, y=j*image.width)
		stones = []
		WINDOW_W_T = WINDOW_W // TILE_SIZE
		WINDOW_H_T = WINDOW_H // TILE_SIZE
		self.fade_stone = pyglet.sprite.Sprite(tiles[self.turn],
													 self.FADE_X, self.FADE_Y,
													 batch = self.batch_fade)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		for i in range(BOARD_H):
			for j in range(BOARD_W):
				new_stone1 = False
				new_stone = False
				x_stone = i*TILE_SIZE+TILE_SIZE 
				y_stone = j*TILE_SIZE+TILE_SIZE
				if ALL_STONES[j,i] == 5.0:
					pass
				else:
					new_stone = pyglet.sprite.Sprite(tiles[ALL_STONES[j,i]],
													 x_stone, y_stone,
													 batch = self.batch			 )
					new_stone.opacity = opacity[ALL_STONES[j,i]]
				if new_stone:
					stones.append(new_stone)					 
		self.batch.draw() 
		if self.FADE_FLAG:
			self.batch_fade.draw()
	
	def make_move(self,y1,x1,pl):
		ALL_STONES[y1-1,x1-1]=pl  # Координаты клеток начинаются с (1,1), а индексы — с (0,0)
		'''
		Ебанутая операция присвоения клетке значения позволяет одинаковым
		действием перейти от нуля к 3 или 4 в зависимости от игрока,
		а также от 3 и 4 к 5, опять же в зависимости от игрока. Из 5 делает 5.
		Парочка abs() нужна из-за восможности питона иметь отрицательные индексы,
		уходя на противоположную сторону поля. А мы не в змейку тут играем.
		Соответственно, пробует проверить все 4 клетки вокруг указанной.
		'''	
		if ALL_STONES[abs(y1-2),x1-1]!=pl: 
			x = ALL_STONES[abs(y1-2),x1-1];
			ALL_STONES[abs(y1-2),x1-1] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
		if ALL_STONES[y1-1,abs(x1-2)]!=pl:
			x = ALL_STONES[y1-1,abs(x1-2)];
			ALL_STONES[y1-1,abs(x1-2)] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
		try:
			if ALL_STONES[y1,x1-1]!=pl:
				x = ALL_STONES[y1,x1-1];
				ALL_STONES[y1,x1-1] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
		except: pass
		try:
			if ALL_STONES[y1-1,x1]!=pl:
				x = ALL_STONES[y1-1,x1];
				ALL_STONES[y1-1,x1] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
		except: pass
		self.turn = self.turn*2%3  # 1->2, 2->1
		self.FADE_FLAG = False #вот это интересно кстати. Если этого не сделать будет
		#раздражающий баг, попробуй если хочешь. Но если я правильно понимаю при 
		#игре на разных машинах этот параметр будет совсем по другому использоваться.
		#print(ALL_STONES)
		self.dispatch_event('on_mademove',x1,y1) # создаётся ивент, который при наличии
		# сетевого клиента перехватывается и высылает ход на сервер. Если клиента нет,
		# то ничего не происходит.
			
	def on_mouse_press(self, x, y, button, modifiers):
		if button == mouse.LEFT:
			x1 = x//TILE_SIZE
			y1 = y//TILE_SIZE
			PLAYER = self.turn
			if 1 <= y1 <= BOARD_H and 1 <= x1 <= BOARD_W:
				if ALL_STONES[y1-1,x1-1]%(PLAYER+2)==0:
					self.make_move(y1,x1,PLAYER)
	
	def on_movereceive(event,self,x,y):
		"""
		'self' стоит не первым из-за того, что событие вызывается извне и сам класс 
		доски вообще в явном виде передаётся при создании события.
		"""
		self.make_move(y,x,self.turn)
	
	def on_mouse_motion(self, x, y, dx, dy):
		if (TILE_SIZE <= x < WINDOW_W-1*TILE_SIZE) and (TILE_SIZE <= y <
														WINDOW_H-1*TILE_SIZE):
			x1 = x//TILE_SIZE 
			y1 = y//TILE_SIZE
			PLAYER = int(self.turn)
			if ALL_STONES[y1-1,x1-1]%(PLAYER+2)==0: 
				'''
			Остаток от деления на номер игрока. Так что рисует только поверх пустой
			или битой собой клетки. Для второго игрока это (0%(2+2) = 0, 4%(2+2) = 0), а для
			первого - (0%(1+2) = 0, 3%(1+2) = 0. Деление любых других чисел на (игрок+2)
			будут иметь остаток.
				'''
				self.FADE_X = (x1) * TILE_SIZE
				self.FADE_Y = (y1) * TILE_SIZE
				self.FADE_FLAG = True				
		self.clear()
	
	def on_key_press(self, symbol, modifiers):
		if symbol == key.ESCAPE:
			self.close()
		if symbol == key.RETURN:
			self.set_fullscreen(True)

Board.register_event_type('on_mademove')
Board.register_event_type('on_movereceive')

"""
Подобное будет в коде клиента для добавления event_handler'а на событие хода
board = Board(...)
def on_mademove(x1,y1):
	client.sendto(...)
board.on_mademove = on_mademove

При получении хода сетевым клиентом будет отправлено событие on_movereceive:
board.dispatch_event('on_movereceive',board,y,x)
Которое объектом класса Board ловится, обновляется матрица, рисуется поле. 'board'
нужно передавать, чтобы можно было в этой функции использовать классовые методы.
"""

if __name__ == "__main__":
	window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
					FONT, ALL_STONES, PLAYER)
	pyglet.app.run()	