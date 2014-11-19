#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-
'''
Kamiken v0.1.2 (unstable)
'''

import pyglet
import sys
from pyglet.window import mouse
from pyglet.window import key
from numpy import zeros
from random import randint
from configparser import ConfigParser

config = ConfigParser()
config.readfp(open("config.ini"))

colors = {	'white'  : (255, 255, 255, 0.3),
	     	'red'    : (255, 0, 0, 0.3),
	     	'blue'   : (0, 0, 255, 0.3),
	     	'board'  : (0.59, 0.54, 0.51, 0.3),
	     	'r_stone': (243, 104, 18, 255),
	     	'b_stone': (14, 193, 225, 255)	  }

'''
Переменные
'''
BOARD_W = int(config.get('settings','board_size_w'))
BOARD_H = int(config.get('settings','board_size_h'))
MSG = 'Press SHIFT+C to connect to server'
TILE_SIZE = 30
FONT = 'Comic Sans MS'
WINDOW_W = BOARD_W * TILE_SIZE + 2 * TILE_SIZE
WINDOW_H = BOARD_H * TILE_SIZE + 2 * TILE_SIZE
BOARD_OPACITY = 40 #opacity 0-255
FADE_STONE_OPACITY = 150
PLAYER = 1.0 #1.0 - red, 2.0 - blue

'''
Изображения
'''
image   = pyglet.resource.image( config.get('images','background')	)
board   = pyglet.resource.image( config.get('images','board')	)
r_stone = pyglet.resource.image( config.get('images','red_stone')	)
b_stone = pyglet.resource.image( config.get('images','blue_stone')	)
r_board = pyglet.resource.image( config.get('images','red_board')	)
b_board = pyglet.resource.image( config.get('images','blue_board')	)
#r_point = pyglet.resource.image( config.get('images','red_point')	)
#b_point = pyglet.resource.image( config.get('images','blue_point')	)

tiles = {		0.0		: board,
				1.0		: r_stone,
				2.0		: b_stone,
				3.0		: r_board,
				4.0		: b_board	     	}

tilenames = {   0.0		: 'board',
				1.0		: 'r_stone',
				2.0		: 'b_stone',			   	# Для вывода в консоль состояния
				3.0		: 'r_point',   				# клетки при клике.
				4.0		: 'b_point',
				5.0		: 'both'      		}

opacity = {     0.0		: BOARD_OPACITY,
				1.0		: '255',
				2.0		: '255',
				3.0		: BOARD_OPACITY*3,
				4.0		: BOARD_OPACITY*3	}
		
player_name = { 1.0 	: 'Red one',
				2.0 	: 'Blue one'      	}

tilehits = {	(1, 0)	: 3,
				(1, 3)	: 3,
				(1, 4)	: 5,
				(1, 5)	: 5,
				(2, 0)	: 4,
				(2, 3)	: 5,
				(2, 4)	: 4,
				(2, 5)	: 5 		  		}
				
'''
Поле
'''
ALL_STONES = zeros([BOARD_W, BOARD_H])

class Board(pyglet.window.Window):

	def __init__(self, WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE, FONT, PLAYER):
		super(Board, self).__init__(width=WINDOW_W, 
		                            height=WINDOW_H, 
		                            caption=('Kamiken player '+player_name[PLAYER]))
		self.set_fullscreen(eval(config.get('settings','fullscreen')))
		self.player = PLAYER
		self.batch_launcher = pyglet.graphics.Batch()
		self.batch = pyglet.graphics.Batch()
		self.batch_fade = pyglet.graphics.Batch()
		self.turn = 1
		self.msg = MSG
		self.label = pyglet.text.Label(text=self.msg, 
		                               font_size=TILE_SIZE-10,
					       				anchor_x = 'center',
					       				font_name=FONT,
					       				color=colors['b_stone'],
					       				x = self.width//2,
					       				y = BOARD_H*TILE_SIZE+TILE_SIZE+5,
					       				batch = self.batch)
		self.fps_display = pyglet.clock.ClockDisplay()
		self.FADE_X = 0
		self.FADE_Y = 0
		self.FADE_FLAG = False
		self.state = "setup" # после коннекта на playing изменяется
			# окно/доска
		self.WIN_W = WINDOW_W
		self.WIN_H = WINDOW_H
		self.BRD_H = BOARD_H
		self.BRD_W = BOARD_W
		self.TILE_SIZE = TILE_SIZE
		self.ALL_STONES = zeros([BOARD_W, BOARD_H])
		

	def on_draw(self):
		"""
		Фоновая картина и лейбл рисуются всегда. Дальше, в зависимости от состояния,
		будет вызываться либо функция прорисовки игры, либо функция прорисовки меню.
		"""
		self.clear()
		self.label.text = self.msg
		IMG_IN_WINDOW_W = self.width//image.width
		IMG_IN_WINDOW_H = self.height//image.height
		if IMG_IN_WINDOW_W == 0:
			IMG_IN_WINDOW_W += 1
		if IMG_IN_WINDOW_H == 0:
			IMG_IN_WINDOW_H += 1
		for i in range(IMG_IN_WINDOW_W*4-1):
			for j in range(IMG_IN_WINDOW_H*4-1):
				image.blit(x=i*image.width, y=j*image.width)
				
		if self.state=="playing": self.draw_game()
		elif self.state=="setup": self.draw_setup()	
	
	def draw_game(self):
		pyglet.gl.glClearColor(*colors['white'])
# 		IMG_IN_WINDOW_W = self.width//image.width
# 		IMG_IN_WINDOW_H = self.height//image.height
# 		if IMG_IN_WINDOW_W == 0:
# 			IMG_IN_WINDOW_W += 1
# 		if IMG_IN_WINDOW_H == 0:
# 			IMG_IN_WINDOW_H += 1
# 		for i in range(IMG_IN_WINDOW_W*4-1):
# 			for j in range(IMG_IN_WINDOW_H*4-1):
# 				image.blit(x=i*image.width, y=j*image.width)
		stones = []
		WINDOW_W_T = self.WIN_W // self.TILE_SIZE
		WINDOW_H_T = self.WIN_H // self.TILE_SIZE
		self.fade_stone = pyglet.sprite.Sprite(tiles[self.turn],
						       self.FADE_X, self.FADE_Y,
						       batch = self.batch_fade)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		
		for i in range(self.BRD_H):
			for j in range(self.BRD_W):
			#	new_stone1 = False
			#	new_stone = False
				x_stone = (i+1)*self.TILE_SIZE
				y_stone = (j+1)*self.TILE_SIZE
				if self.ALL_STONES[j,i] < 5.0:
					new_stone = pyglet.sprite.Sprite(tiles[self.ALL_STONES[j,i]],
									 x_stone, y_stone,
									 batch = self.batch         )
					new_stone.opacity = opacity[self.ALL_STONES[j,i]]
					stones.append(new_stone)
		self.batch.draw()
		if self.FADE_FLAG:
			self.batch_fade.draw()

	def draw_setup(self):
		self.msg = "shift-c нажми"
		self.batch.draw()
		pass
		
	def make_move(self,x1,y1,pl):
		if self.turn!=pl:	return		# Если повторный вызов функции (5 одинаковых 
										# сообщений же клиент получет), то мгновенный выход
		self.ALL_STONES[y1,x1]=pl
		for i in range(-1,2):
			for j in range(-1,2):
				if abs(i - j) == 1:
					try:
						if self.ALL_STONES[abs(y1+i),abs(x1+j)]!=pl:
							x = self.ALL_STONES[abs(y1+i),abs(x1+j)];
							self.ALL_STONES[abs(y1+i),abs(x1+j)] = tilehits[pl,x]
					except: pass
		self.turn = self.turn*2%3  # 1->2, 2->1
		self.FADE_FLAG = False
		self.label_update()
		
	def on_mouse_press(self, x, y, button, modifiers):
		if button == mouse.LEFT:
			
			x1 = x//TILE_SIZE - 1
			y1 = y//TILE_SIZE - 1
			if 0 <= y1 < self.BRD_H and 0 <= x1 < self.BRD_W:
				if self.ALL_STONES[y1,x1]%(self.player+2)==0 and self.turn==self.player:
					self.make_move(x1,y1,self.player)
					self.dispatch_event('on_mademove',self.player,x1,y1) # создаётся ивент, который
					# при наличии сетевого клиента перехватывается и высылает ход на сервер.
					# Если клиента нет, то ничего не происходит.


	def on_movereceive(event,self,player,x,y):
		"""
		'self' стоит не первым из-за того, что событие вызывается извне и сам класс
		доски вообще в явном виде передаётся при создании события.
		"""
		if player==0:
			self.label_update()
		self.make_move(x,y,player)

	def on_mouse_motion(self, x, y, dx, dy):
		if (self.TILE_SIZE <= x < self.WIN_W-self.TILE_SIZE) and (self.TILE_SIZE <= y <
									  self.WIN_H-self.TILE_SIZE):
			x1 = x//self.TILE_SIZE - 1
			y1 = y//self.TILE_SIZE - 1
			if self.ALL_STONES[y1,x1]%(self.player+2)==0 and self.turn==self.player:
				'''
			Остаток от деления на номер игрока. Так что рисует только поверх пустой
			или битой собой клетки. Для второго игрока это (0%(2+2) = 0, 4%(2+2) = 0), а для
			первого - (0%(1+2) = 0, 3%(1+2) = 0. Деление любых других чисел на (игрок+2)
			будут иметь остаток.
				'''
				self.FADE_X = (x1+1) * TILE_SIZE
				self.FADE_Y = (y1+1) * TILE_SIZE
				self.FADE_FLAG = True
		self.clear()

	def on_key_press(self, symbol, modifiers):
		if symbol == key.ESCAPE:
			self.close()
		if symbol == key.RETURN:
			self.set_fullscreen(self.fullscreen^True)
		if symbol == key.C and modifiers and key.MOD_SHIFT:
			self.dispatch_event('on_reqconnect')
			self.state="playing"
			self.label_update()
#			self.msg = "Waiting for second player..."
		if symbol == key.Q and key.MOD_SHIFT: 	# Для аутизм-режима
			self.player = self.player*2%3
		if symbol == key.T and key.MOD_SHIFT:	# тесты-хуесты. Для смены размера поля
#			self.ALL_STONES = zeros([5, 5])		# нужно изменять диапазоны for лупов,
			self.width=self.width/2				# и проверки on_mouse_motion, чтобы
												# не выдавало ошибок при наведении на
												# убранные клетки, индексов которых уже нет

	def label_update(self):
		if self.turn==self.player:
			self.msg = 'Your move!'
		else:
			self.msg = "Opponent's move!"

Board.register_event_type('on_mademove')
Board.register_event_type('on_movereceive')
Board.register_event_type('on_reqconnect')

"""
Подобное будет в коде ланчера для добавления event_handler'а на событие хода
board = Board(...)
def on_mademove_event_handler(x1,y1):
	client.sendto(...)
board.on_mademove = on_mademove_event_handler

При получении хода сетевым клиентом будет отправлено событие on_movereceive:
board.dispatch_event('on_movereceive',board,y,x)
Которое объектом класса Board ловится, обновляется матрица, рисуется поле. 'board'
нужно передавать, чтобы можно было в этой функции использовать классовые методы.
"""

if __name__ == "__main__":
	window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, 
	               MSG, TILE_SIZE, FONT, PLAYER)
	pyglet.app.run()
