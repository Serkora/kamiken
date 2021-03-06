#!/usr/bin/env python3
#  - * -  coding: UTF - 8  - * - 
'''
Kamiken v0.3.0
'''

import pyglet
import sys
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from numpy import zeros, where, cos, arccos, pi
import numpy as np
from math import copysign
from random import randint
from configparser import ConfigParser
from threading import Thread
import time
from copy import copy

config = ConfigParser()
config.readfp(open("config.ini"))

colors = {	'white'  : (255, 255, 255, 0.3),
	     	'red'    : (255, 0, 0, 0.3),
	     	'blue'   : (0, 0, 255, 0.3),
	     	'board'  : (0.59, 0.54, 0.51, 0.3),
	     	'r_stone': (243, 104, 18, 255),
	     	'b_stone': (14, 193, 225, 255),
	     	'textb'	 : (14, 193, 225, 255),
	     	'textr'	 : (243, 104, 18, 255)}

'''
Переменные
'''
BOARD_W = int(config.get('settings','board_size_w'))
BOARD_H = int(config.get('settings','board_size_h'))
MSG = 'KAMI~!!'
TILE_SIZE = 24
SQUARE_SIZE = 30
FONT = 'Comic Sans MS'
WINDOW_W = int(config.get('settings', 'resolution').split("x")[0])
WINDOW_H = int(config.get('settings', 'resolution').split("x")[1])
FULLSCREEN = eval(config.get('settings','fullscreen'))
BOARD_OPACITY = 40 #opacity 0 - 255
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
mp_select = pyglet.resource.image( config.get('images','mp_select')	)
sp_select = pyglet.resource.image( config.get('images','sp_select')	)

# Выставляет привязку начала координат к центрам спрайтов
board.anchor_x, board.anchor_y = board.width//2, board.height//2
r_stone.anchor_x, r_stone.anchor_y =r_stone.width//2, r_stone.height//2
b_stone.anchor_x, b_stone.anchor_y = b_stone.width//2, b_stone.height//2
r_board.anchor_x, r_board.anchor_y =r_board.width//2, r_board.height//2
b_board.anchor_x, b_board.anchor_y = b_board.width//2, b_board.height//2
mp_select.anchor_x, mp_select.anchor_y = mp_select.width//2, mp_select.height//2
sp_select.anchor_x, sp_select.anchor_y = sp_select.width//2, sp_select.height//2


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
				3.0		: BOARD_OPACITY * 3,
				4.0		: BOARD_OPACITY * 3	}
		
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

def write_config(board):
	"""
	Записывает в конфиг последние настройки размера окна и был ли выбран
	полноэкранный режим. Если был полноэкранный режим, то размеры окна не изменяются,
	для удобного выхода в оконный режим, а не созданий окна с разрешением экрана.
	"""
	config['settings']['fullscreen'] = str(board.fullscreen)
	if not board.fullscreen:
		config['settings']['resolution'] = str(board.width)+"x"+str(board.height)
	with open('config.ini','w') as configfile:
		config.write(configfile)

def texture_set_mag_filter_nearest( texture ): #функция, преобразующая изображение в текстуру OpenGL со всякими фильтрами
	glBindTexture( texture.target, texture.id  )
	glTexParameteri( texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
	glBindTexture( texture.target, 0 )		


class TextWidget(object):
    """
    Поле ввода текста. Работает магическим образом, так как некоторые вещи,
    которые должны быть работоспособными, отказываются правильно исполняться.
    """
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), 
            					dict(color=colors['textb'],font_size=20))
        font = FONT
        height = 30

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y
        
        self.focus = None

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)
                
    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0
        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)
            
    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

class GameMenu(object):
	"""
	Игровое меню. Содержит в себе все пункты меню. Передаваемые в аргументах
	координаты являются положением верхнего левого угла, чтобы можно было 
	легко располагать как справа, так и снизу от поля.
	Позволяет иметь вертикальное или горизонтальное расположение кнопок.
	Аргументом height передаётся высота окна/экрана, чтобы соответственно изменять
	размер шрифта (1/40 от высоты), делается это в place_buttons.
	(self.height — lambda-функция)
	self.x и self.y — функции определения отправной точки, передаются в 
	виде lambda-функции при создании объекта этого класса.
	board — доска. Нужно для создания событий по клику на клавиши.
	batch — графический batch, в котором это меню нужно будет рисовать.
	"""
	def __init__(self, x, y, height, board, batch, orientation = "vertical"):
		self.orientation = orientation
		self.x = x
		self.y = y
		self.batch = batch
		self.height = height
		self.board = board
		self.create_buttons()
		self.place_buttons()
	
	def create_buttons(self):
		"""
		В self.button_names записаны названия (текст) кнопок, далее for луп создаёт
		по кнопкке на каждый из элементов списка, присваивая атрибут в видео строчного
		написания текста кнопки без пробелов. Затем кнопка добавляюется в список уже
		пиглетовских объектов, которые затем используется в лупах расположения.
		"""
		self.button_names = ['Skip turn', 'Save game', 'Finish game', 'Settings',
								'Disconnect', 'Quit']
		self.buttons = []
		for button in self.button_names:
			setattr(self, button.lower().replace(" ",""), pyglet.text.Label(
				button, anchor_x="left", anchor_y="top", font_name=FONT,
				color=colors['textb'], batch=self.batch))
			self.buttons.append(eval("self."+button.lower().replace(" ","")))
	
	def place_buttons(self):
		"""
		Располагает кнопки друг под другом или в одну строку. Размер шрифта высчитывается
		именно тут, чтобы одной этой функцией легко перерисовывать кнопки при изменении 
		размера окна.
		В горизонтальном расположении первая кнопка ставится вне лупа, потому что
		расположение кнопок зависит от предыдущей.
		self.x() и self.y() — функции, высчитывающие "нулевую" точку меню.
		"""
		self.fontsize = self.height()/40
		if self.orientation == "vertical":
			for i in range(0,len(self.buttons)):
				self.buttons[i].font_size = self.fontsize
				self.buttons[i].x = self.x()
				self.buttons[i].y = self.y() - self.fontsize * (i*2)

		elif self.orientation == "horizontal":
			self.buttons[0].x, self.buttons[0].y = self.x(), self.y()
			self.buttons[0].font_size = self.fontsize
			for i in range(1, len(self.buttons)):
				self.buttons[i].font_size = self.fontsize
				self.buttons[i].y = self.y()
				self.buttons[i].x = self.buttons[i-1].x + \
					self.buttons[i-1].content_width + self.fontsize
			
	def highlight(self, x, y):
		"""
		Меняет цвет выделенного мышкой пункта меню.
		"""
		for button in self.buttons:
			if button.x <= x <= button.x + button.content_width and \
				button.y - button.content_height <= y <= button.y:
					button.color = colors['textr']
			else:
				button.color = colors['textb']
	
	def button_press(self, x, y):
		"""
		Если была нажата какая-то кнопка, передаёт текст этой кнопки в отдельную
		функцию, которая и будет совершать действие, в зависимости от кнопки.
		"""
		for button in self.buttons:
			if button.x <= x <= button.x + button.content_width and \
				button.y - button.content_height <= y <= button.y:
					self.button_action(button.text)

	def button_action(self, button):
		"""
		По названию (тексту) кнопки производится соответствующая операция.
		"""
		if button == "Skip turn":
			if self.board.turn == self.board.player:
				for i in range(0,5):
						pyglet.clock.schedule_once(
						lambda x: self.board.dispatch_event('on_mademove',self.board.player,-1,-1), (i*0.1)
						)
				self.board.turn = self.board.turn*2%3
				self.board.skips += 1
				self.board.label_update()
				if self.board.skips == 2:
					self.board.finish_game()
		if button == "Restart":
			self.board.start_game()
			self.skipturn.text = "Skip Turn"
# 			for i in range(0,5):
# 				pyglet.clock.schedule_once(
# 				lambda x: self.board.dispatch_event('on_mademove',self.board.player,"restart","restart"), (i*0.1)
# 				)
		elif button == "Save game":
			pass
		elif button == "Finish game":
			self.board.finish_game()
		elif button == "Settings":
			pass
		elif button == "Disconnect":
			self.board.finish_game()
			self.board.state = "setup"
			self.board.dispatch_event('on_disconnect')
		elif button == "Quit":
			self.board._quit()

class Board(pyglet.window.Window):

		###### Важные и/или "системные" функции ######

	def __init__(self, BOARD_W, BOARD_H, WINDOW_W, WINDOW_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT):
			# Изначальные игровые параметры
		self.player = 1
		self.turn = 1
		self.TILE_SIZE = TILE_SIZE
		self.SQUARE_SIZE = SQUARE_SIZE
		self.BRD_H = BOARD_H
		self.BRD_W = BOARD_W
		self.scale = self.TILE_SIZE/r_stone.width
		self.state = "setup" # после коннекта на playing изменяется
		self.gametype = "multiplayer"
		self.skip = 0 # Считает количество пропущеных подряд ходов. 2 — конец игры.
			# окно и отступы
		self.WIN_W = WINDOW_W
		self.WIN_H = WINDOW_H
		super(Board, self).__init__(width=self.WIN_W, height=self.WIN_H, 
									caption=('Kamiken'), vsync=False)
		self.set_fullscreen(FULLSCREEN)
		self.margin_v = (self.height - self.SQUARE_SIZE * self.BRD_H) // 2
		self.margin_h = (self.width - self.SQUARE_SIZE * self.BRD_W) // 4
			# графические параметры
		self.batch_game = pyglet.graphics.Batch()
		self.batch_startup = pyglet.graphics.Batch()
		self.batch_menu = pyglet.graphics.Batch()
		self.batch_fade = pyglet.graphics.Batch()
		self.stones = []
		self.FADE_X = 0
		self.FADE_Y = 0
		self.FADE_FLAG = False
		self.pulse_opacity = 40
		self.pulse_stone = (-1,-1)
		self.pulse_pos = True
		self.fps_display = pyglet.clock.ClockDisplay()
			# лейблы / текст
		self.msg = MSG
		self.label = pyglet.text.Label(
			text=self.msg, font_size=TILE_SIZE - 10, anchor_x='center', font_name=FONT,
			color=colors['b_stone'], x=self.width//2, y=self.height - 25,
			batch = self.batch_game)
		self.startuplabels()

			# Для тестов #
		self.i = 0
		self.time1 = time.clock()

	def _quit(self):
		self.dispatch_event('on_disconnect')
		write_config(self)
		self.close()

		###### Графические функции ######
	
	def on_draw(self):
		"""
		Фоновая картина и лейбл рисуются всегда. Дальше, в зависимости от состояния,
		будет вызываться либо функция прорисовки игры, либо функция прорисовки меню,
		либо конец игры и вывод счёта. 		
		"""
		self.clear()
		pyglet.gl.glClearColor( * colors['white'])
		self.label.text = self.msg
		IMG_IN_WINDOW_W = self.width//image.width
		IMG_IN_WINDOW_H = self.height//image.height
		if IMG_IN_WINDOW_W == 0:
			IMG_IN_WINDOW_W  += 1
		if IMG_IN_WINDOW_H == 0:
			IMG_IN_WINDOW_H  += 1
		for i in range(IMG_IN_WINDOW_W * 4 - 1):
			for j in range(IMG_IN_WINDOW_H * 4 - 1):
				image.blit(x=i * image.width, y=j * image.width)
		self.fps_display.draw()
		
		if self.state=="playing": self.draw_game()
		elif self.state=="setup": self.draw_setup()	
		elif self.state=="finish": self.draw_finish()
	
	def draw_game(self):
		"""
		Функция обновления поля. Меняет координаты полупрозрачного камня, показывающего,
		куда будет совершён ход. рисует меню (может обновиться в любое время) и 
		само игровое поле.
		Первый камень появляется с непрозрачностью 40, плавно увеличивается, и начинает
		колебаться между 160 и 250.
		"""
		self.fade_stone.x = self.FADE_X
		self.fade_stone.y = self.FADE_Y
		if self.FADE_FLAG:
			self.batch_fade.draw() 
		self.stones[self.pulse_stone[0]][self.pulse_stone[1]].opacity = self.pulse_opacity
		self.batch_menu.draw()
		self.batch_game.draw()
	
	def draw_boardinit(self):
		"""
		Функция инициализации поля. Рисует полупрозрачные "пустые" клетки, создаёт список
		графический объектов-спрайтов, которыми затем можно манипулировать во время игры.
		Начало поля начинается с отступами self.margin_h/v
		Центр камня находится в середине "клетки", размер которой self.SQUARE_SIZE.
		Соответственно, разница между размером тайла и размером клетки будет пустым 
		пространством для визуального разделения клеток.
		(i+0.5) и (j+0.5) нужны потому что anchor спрайтов в центре, а не нижнем углу.
		"""
		self.stones = []
		for i in range(self.BRD_H):
			self.stonesj = []
			for j in range(self.BRD_W):
				x_stone = (i + 0.5) * self.SQUARE_SIZE + self.margin_h
				y_stone = (j + 0.5) * self.SQUARE_SIZE + self.margin_v
				new_stone = pyglet.sprite.Sprite(
					tiles[0], x_stone, y_stone, batch=self.batch_game
				)
				new_stone.scale = self.scale
				new_stone.opacity = opacity[0]
				self.stonesj.append(new_stone)
			self.stones.append(self.stonesj)
		self.fade_stone = pyglet.sprite.Sprite(
			tiles[self.player], self.FADE_X, self.FADE_Y, batch = self.batch_fade
		)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		self.fade_stone.scale = self.scale
		self.batch_game.draw()
	
	def draw_boardinit2(self):
				## СТАРАЯ ВЕРСИЯ, ОСТАЁТСЯ ТУТ НА СЛУЧАЙ НЕПРЕДВИДЕННЫХ ОБСТОЯТЕЛЬСТВ ##
		"""
		Функция инициализации поля. Рисует полупрозрачные "пустые" клетки, создаёт список
		спрайтов.
		Начало поля начинается с конца отступов self.margin_h/v
		Так как прозрачные области были из спрайтов камней убраны, каждый камень
		рисуется с дополнительным отступом: разницей между размером спрайта и необходимым
		размером одной клетки.
		(i+0.5) и (j+0.5) нужны потому что anchor спрайтов в центре, а не нижнем углу.
		"""
		
		self.stones = []
		for i in range(self.BRD_H):
			self.stonesj = []
			for j in range(self.BRD_W):
				stone = self.ALL_STONES[j,i]
				x_stone = (i + 0.5) * self.SQUARE_SIZE + self.margin_h
				y_stone = (j + 0.5) * self.SQUARE_SIZE + self.margin_v
				if stone < 5:
					new_stone = pyglet.sprite.Sprite(
						tiles[stone], x_stone, y_stone, batch=self.batch_game
					)
					new_stone.scale = self.scale
					if (i,j) == self.pulse_stone:	# ПУЛЬСАЦИЯ ОТКЛЮЧЕНА
						new_stone.opacity = self.pulse_opacity
					else:
						try:
							new_stone.opacity = opacity[stone]
						except:
							self.msg = "You have won the lottery!"
					self.stonesj.append(new_stone)
			self.stones.append(self.stonesj)
		self.fade_stone = pyglet.sprite.Sprite(
			tiles[self.turn], self.FADE_X, self.FADE_Y, batch = self.batch_fade
		)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		self.fade_stone.scale = self.scale
		self.batch_game.draw()
	
	def draw_boardinit3(self):
				## НЕРАБОТАЮЩАЯ ВЕРСИЯ ##
		""" 
		Была попытка создать один спрайт и потом его копировать — не взлетело,
		ничего не рисуется, хотя спрайты (и даже разные) создаются. Один только "stone"
		рисуется, при этом на координатах последнего new_stone'а — то есть верхний
		правый угол. Если перед отрисовкой сделать stone.x = 10 или self.stones[0].x = 10,
		то камень рисуется именно в (10,50), несмотря на то, что с 'y' я ничего делал.
		Вывод — необходимо иметь столько объектов-спрайтов, сколько нужно нарисовать.
		"""
		stone = pyglet.sprite.Sprite(
						tiles[2], 50, 50, batch=self.batch_game
					)
		stone.scale = self.scale
		stone.opacity = opacity[2]
		self.stones = []
		self.stones.append(stone)
		for i in range(self.BRD_H):
			self.stonesj = []
			for j in range(self.BRD_W):
				#stone = self.ALL_STONES[j,i]
				new_stone = copy(stone)
				print(new_stone.image)
				x_stone = (i + 0.5) * self.SQUARE_SIZE + self.margin_h
				y_stone = (j + 0.5) * self.SQUARE_SIZE + self.margin_v
				new_stone.x = x_stone
				new_stone.y = y_stone
				#if stone < 5:
				#	new_stone = pyglet.sprite.Sprite(
				#		tiles[stone], x_stone, y_stone, batch=self.batch_game
				#	)
				#	new_stone.scale = self.scale
				#	if (i,j) == self.pulse_stone:	# ПУЛЬСАЦИЯ ОТКЛЮЧЕНА
				#		new_stone.opacity = self.pulse_opacity
				#	else:
				#		try:
				#			new_stone.opacity = opacity[stone]
				#		except:
				#			self.msg = "You have won the lottery!"
				self.stonesj.append(new_stone)
			self.stones.append(self.stonesj)
		print(self.stones)
		self.fade_stone = pyglet.sprite.Sprite(
			tiles[self.turn], self.FADE_X, self.FADE_Y, batch = self.batch_fade
		)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		self.fade_stone.scale = self.scale
		self.batch_game.draw()		

	def draw_setup(self):
		xp1 = self.width//2 - self.TILE_SIZE * 3
		yp1 = self.height//2.5
		xp2 = self.width//2 + self.TILE_SIZE * 3
		yp2 = self.height//2.5
		pl1 = pyglet.sprite.Sprite(tiles[abs(self.player - 2)], xp1, yp1, batch=self.batch_startup)
		pl2 = pyglet.sprite.Sprite(tiles[self.player * 2 - 2], xp2, yp2, batch=self.batch_startup)
		pl1.scale = self.scale * 3; pl2.scale = self.scale * 3
		if abs(self.player - 2) == 1: pl2.opacity = 50
		else: pl1.opacity = 50

		if self.gametype == "multiplayer": 
			mp_sel = pyglet.sprite.Sprite(mp_select, self.mp_label.x, self.mp_label.y,
											batch=self.batch_startup)
		else:
			sp_sel = pyglet.sprite.Sprite(sp_select, self.sp_label.x, self.sp_label.y,
											batch=self.batch_startup)
		self.batch_startup.draw()
		pass

	def draw_finish(self):
		self.draw_game()

	def pulsation(self,trash):
		"""
		Переделано для увеличения производительности.
		"""
		if self.pulse_stone == (-1,-1):
			self.pulse_opacity = 40
		elif self.pulse_pos:
			self.pulse_opacity = self.pulse_opacity + 10
			if self.pulse_opacity >= 250: self.pulse_pos = False
		else:
			self.pulse_opacity = self.pulse_opacity - 10
			if self.pulse_opacity <= 160: self.pulse_pos = True

		###### Добавление или удаление элементов, перерасчёт координат ######
	
	def startuplabels(self):
		"""
		Создаёт лейблы/виджеты настроек.
		"""
		self.brdlabel = pyglet.text.Label(
			"Board size", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['textb'], x=self.width/2 - 40, y=self.height/1.35, 
			batch = self.batch_startup)
		self.boardtxt = TextWidget(str(BOARD_H), self.width/2 + 60, self.height/1.35 - 7.5, 
										50, self.batch_startup)
		self.sp_label = pyglet.text.Label(
			"Single Player", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['textb'], x=self.width/2-70, y=self.height/1.6, 
			batch = self.batch_startup)
		self.mp_label = pyglet.text.Label(
			"Multiplayer", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['textb'], x=self.width/2+70, y=self.height/1.6, 
			batch = self.batch_startup)
		
	def update_coordinates(self):
		"""
		Подбирает размер окна под размер поля; изменяет отступы, если размер окна
		изменился, чтобы поле осталось в центре. Если оконный режим — меняет размер окна.
		Также меню присваиватся новые координаты, и обновляется расположение кнопок.
		"""
		self.SQUARE_SIZE = (self.height - 60)//self.BRD_H
		self.TILE_SIZE = 0.8 * self.SQUARE_SIZE
		self.scale = self.TILE_SIZE/r_stone.width
		self.margin_v = (self.height - self.SQUARE_SIZE*self.BRD_H) // 2
		self.margin_h = (self.width - self.SQUARE_SIZE*self.BRD_W) // 4
		self.labels_redraw()
		if hasattr(self, 'game_menu'):
			self.game_menu.place_buttons()
		self.FADE_FLAG = False # скорее всего, курсор будет уже на другом местеЙ
		if self.state == "playing":
			# Изменяет параметры спрайтов.
			self.fade_stone.scale = self.scale
			for i in range(len(self.stones)):
				for j in range(len(self.stones[0])):
					self.stones[i][j].x = (i + 0.5) * self.SQUARE_SIZE + self.margin_h
					self.stones[i][j].y = (j + 0.5) * self.SQUARE_SIZE + self.margin_v
					self.stones[i][j].scale = self.scale
				

	def label_update(self):
		if self.state == "playing":
			if self.turn==self.player:
				self.msg = 'Your turn!'
			else:
				self.msg = "Opponent's turn!"

	def labels_redraw(self):
		"""
		Проверяет, какие из лейблов/полей текста присутствуют (какие-то удаляются 
		после началаигры, какие-то, наоборот, добавляются) и ставит на нужное место 
		при изменении размера окна или переходе в полноэкранный режим.
		"""
		if hasattr(self, 'label'):
			self.label.x = self.width//2
			self.label.y = self.height - 25
		if hasattr(self, 'boardtxt'):
			self.boardtxt.layout.x = self.width//2 + 60
			self.boardtxt.layout.y = self.height/1.35 - 10
		if hasattr(self, 'brdlabel'):
			self.brdlabel.x = self.width/2 - 40
			self.brdlabel.y = self.height/1.35
		if hasattr(self, 'sp_label'):
			self.sp_label.x = self.width/2-70
			self.sp_label.y = self.height/1.6
		if hasattr(self, 'mp_label'):
			self.mp_label.x = self.width/2+70
			self.mp_label.y = self.height/1.6
		pass

		###### Игровые функции ######

	def start_game(self):
		"""
		Из __init__ было сюда перенесено, чтобы изменить окно/доску после выбора в меню.
		Снова вернулись к квадратной. Из TextWidget'а берётся введённое число, 
		а дальше всё как и раньше.
		Снова вызывается функция обновления размера окна, отступов, координат лейблов.
		В стек добавляется функция, изименяющая прозрачность последнего хода каждые 1/30с.
		В принципе, туда можно добавить и другую анимацию. ОТКЛЮЧЕНО
		menu_def_x/y вынесены для удобности редактирования/восприятия.
		Используется lambda для того, чтобы menu.x (отправная точна координат отедльных
		кнопок) было функцией, меняющей значение в зависимости от размеров окна 
		без эксплицитного объявления этого изменения.
		self.draw_boardinit() — функция, создающая нужно количество спрайтов для "доски"
		"""
		boardsize = int(self.boardtxt.document.text)
		self.BRD_H = boardsize
		self.BRD_W = boardsize
		self.ALL_STONES = zeros([self.BRD_W, self.BRD_H])
		if not hasattr(self, "game_menu"):
			menu_def_x = lambda: self.margin_h + (self.BRD_H+0.5) * self.SQUARE_SIZE
			menu_def_y = lambda: self.height - self.margin_v
			self.game_menu = GameMenu(menu_def_x, menu_def_y, height=lambda: self.height,
										board=self, batch=self.batch_menu,
										orientation = "vertical")
		self.update_coordinates()
		self.draw_boardinit()
		if self.gametype == "multiplayer":
			self.dispatch_event('on_reqconnect')
		pyglet.clock.schedule_interval(self.pulsation,1/30)
		self.state = "playing"
	
	def finish_game(self):
		score_r = len(where(self.ALL_STONES==3)[0])
		score_b = len(where(self.ALL_STONES==4)[1])
		self.msg = "Red: "+str(score_r)+"  Blue: "+str(score_b)
		pyglet.clock.unschedule(self.pulsation)
		self.pulse_opacity = 40
		self.pulse_stone = (-1,-1)
		self.turn = 1
		self.state = "finish"
		self.game_menu.skipturn.text = "Restart"
	
	def make_move(self,x1,y1,pl):
		"""
		Проверяет, действитеьно ли сейчас ход того игрока, кем была вызвана функция,
		или есть ли уже камень на том месте, на которое кликнули — если да, то
		возвращает из функции. Проверка полезна из-за дублирования передаваемых и 
		получаемых клиентом сообщений.
		Смотрит 4 клетки вокруг той, на которую кликнули, и меняет их значения 
		соответственно правилам.
		Если зачение матрицы равно 5 — удаляет спрайт из буфера (оставляя в списке,
		чтобы порядок не сбивался). В остальных случаях просто меняет изображение.
		Если предыдущее значение координат пульсирующего камня была не (-1,-1) (то есть,
		был сделан уже второй ход), то убирается прозрачность с этого камня. Если этого
		не делать, то камень запомнит то значение, во время которого был совершён ход.
		"""
		if self.turn != pl or self.ALL_STONES[y1,x1] == pl:	return
		self.ALL_STONES[y1,x1] = pl
		self.stones[x1][y1].image = tiles[pl]
		self.stones[x1][y1].opacity = opacity[pl]
		for i in range(-1,2):
			for j in range(-1,2):
				if abs(i - j) == 1:
					try:
						if self.ALL_STONES[abs(y1 + i),abs(x1 + j)] != pl:
							x = self.ALL_STONES[abs(y1 + i),abs(x1 + j)];
							self.ALL_STONES[abs(y1 + i),abs(x1 + j)] = tilehits[pl,x]
							x = self.ALL_STONES[abs(y1 + i),abs(x1 + j)];
							if x == 5:
								self.stones[abs(x1 + j)][abs(y1 + i)].delete()
							else:
								self.stones[abs(x1 + j)][abs(y1 + i)].image = tiles[x]
								self.stones[abs(x1 + j)][abs(y1 + i)].opacity = opacity[x]
					except: pass
		self.turn = self.turn * 2%3  # 1 - >2, 2 - >1
		self.FADE_FLAG = False
		if self.pulse_stone != (-1,-1):
			self.stones[self.pulse_stone[0]][self.pulse_stone[1]].opacity = 255
		self.pulse_stone = (x1,y1)
		self.skips = 0 # Сбрасывает счётчик пропусков.
		self.label_update()

	def mouse_motion_setup(self,x,y):
		"""
		Следит за курсором и выставляет номер игрока, если курсор наводится на один 
		из камней.
		"""
		xp1 = self.width//2 - self.TILE_SIZE * 4.5
		yp1 = self.height//2.5 - self.TILE_SIZE * 1.5
		xp2 = self.width//2 + self.TILE_SIZE * 1.5
		yp2 = self.height//2.5 - self.TILE_SIZE * 1.5
		if xp1 <= x <= xp1 + self.TILE_SIZE * 3 and yp1 <= y <= yp1 + self.TILE_SIZE * 3:
			self.player = 1
		if xp2 <= x <= xp2 + self.TILE_SIZE * 3 and yp2 <= y <= yp2 + self.TILE_SIZE * 3:
			self.player = 2

	def mouse_motion_play(self,x,y):
		x1 = (x - self.margin_h)//self.SQUARE_SIZE
		y1 = (y - self.margin_v)//self.SQUARE_SIZE
		if 0 <= y1 < self.BRD_H and 0 <= x1 < self.BRD_W:
			if self.ALL_STONES[y1,x1]%(self.player + 2)==0 and self.turn==self.player:
				"""
				Остаток от деления на номер игрока. Так что рисует только поверх пустой
				или битой собой клетки. Для второго игрока это (0%(2 + 2) = 0, 
				4%(2 + 2) = 0),  а для первого - (0%(1 + 2) = 0, 3%(1 + 2) = 0. 
				Деление любых других чисел на (игрок + 2) будут иметь остаток.
				(x1/y1 + 0.5) опять же из-за центрирования спрайтов.
				"""
				self.FADE_X = (x1 + 0.5) * self.SQUARE_SIZE + self.margin_h
				self.FADE_Y = (y1 + 0.5) * self.SQUARE_SIZE + self.margin_v
				self.FADE_FLAG = True
		else: 
			self.FADE_FLAG = False
	
	def mouse_press_setup(self,x,y):
		"""
		Если клик был по полю для ввода размера доски, то появляется каретка и
		можно изменять текст. Если вне — каретка пропадает, писать нельзя.
		Если был клик по любому из камней выбора игрока, начинается игра (номер игрока
		уже выбран при наведении курсора на камень), запускаются функции изменения 
		размера доски, окна и т.д.
		"""
		if self.boardtxt.hit_test(x, y):
			self.boardtxt.focus = True
			self.boardtxt.caret.visible = True
		else: 
			self.boardtxt.focus = None
			self.boardtxt.caret.visible = False

		xp1 = self.width//2 - self.TILE_SIZE * 4.5
		yp1 = self.height//2.5 - self.TILE_SIZE * 1.5
		xp2 = self.width//2 + self.TILE_SIZE * 1.5
		yp2 = self.height//2.5 - self.TILE_SIZE * 1.5

		xsp = self.sp_label.x - self.sp_label.content_width/2
		ysp = self.sp_label.y - self.sp_label.content_height/2
		xmp = self.mp_label.x - self.mp_label.content_width/2
		ymp = self.mp_label.y - self.mp_label.content_height/2

		if xsp <= x <= xsp + self.sp_label.content_width \
			and ysp <= y <= ysp + self.sp_label.content_height:
				self.gametype = "singleplayer"
		elif xmp <= x <= xmp + self.mp_label.content_width \
			and ymp <= y <= ymp + self.mp_label.content_height:
				self.gametype = "multiplayer"
		
		if xp1 <= x <= xp1 + self.TILE_SIZE * 3 and yp1 <= y <= yp1 + self.TILE_SIZE * 3 \
			or xp2 <= x <= xp2 + self.TILE_SIZE * 3 and yp2 <= y <= yp2 + self.TILE_SIZE * 3:
				self.start_game()
				self.msg = "Waiting for second player..."
	
	def mouse_press_play(self,x,y):
		"""
		При ходе создаётся событие, которе при наличии сетевого клиента перехватывается
		и высылает ход на сервер. Повторяется 5 раз с интервалом в 100мс.
		Если клиента нет, камень ставится на поле и больше ничего не происходит.
		"""
		x1 = (x - self.margin_h)//self.SQUARE_SIZE
		y1 = (y - self.margin_v)//self.SQUARE_SIZE
		if 0 <= y1 < self.BRD_H and 0 <= x1 < self.BRD_W:
			if self.ALL_STONES[y1,x1]%(self.player + 2) == 0 and self.turn == self.player:
				self.make_move(x1,y1,self.player)
				for i in range(0,5):
					pyglet.clock.schedule_once(
					lambda x: self.dispatch_event('on_mademove',self.player,x1,y1), (i*0.1)
					)

		###### Обработчики событий ######
	def on_movereceive(event,self,player,x,y):
		"""
		'self' стоит не первым из - за того, что событие вызывается извне и сам класс
		доски вообще в явном виде передаётся при создании события.
		"""
		if player!=0 and x >= 0 and y >= 0:
			self.make_move(x,y,player)
		elif player == self.turn and x == -1 and y == -1:
			self.turn = self.turn*2%3
			self.skips += 1
			if self.skips == 2:
				self.finish_game()
			self.label_update()
		
	def on_mouse_press(self, x, y, button, modifiers):
		"""
		В зависимости от этапа игры по клику вызываются разные функции.
		"""
		if button == mouse.LEFT and self.state == "playing":
			self.mouse_press_play(x,y) 
			self.game_menu.button_press(x,y)
		elif button ==mouse.LEFT and self.state == "finish":
			self.game_menu.button_press(x,y)
		elif button == mouse.LEFT and self.state == "setup":
			self.mouse_press_setup(x,y)

	def on_mouse_motion(self, x, y, dx, dy):
		"""
		Чтобы не забивать это обработчик событий кучей условий (а их будет много), 
		присвоений и прочей фигни, решил вынести всё в отедльные функции, а тут
		только вызывать то, что нужно, в зависимсоти от состояния игры.
		"""
#		self.msg = str(x)+"  "+str(y)
		if self.state == "playing":
			self.mouse_motion_play(x,y)
			self.game_menu.highlight(x,y)
		elif self.state == "finish":
			self.game_menu.highlight(x,y)
		elif self.state == "setup":
			self.mouse_motion_setup(x,y)	
	
	def on_text(self,text):
		if self.state == "setup" and self.boardtxt.focus:
			self.boardtxt.caret.on_text(text)

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.state == "setup" and self.boardtxt.focus:
			self.boardtxt.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

	def on_text_motion(self, motion):
		if self.state == "setup" and self.boardtxt.focus:
			self.boardtxt.caret.on_text_motion(motion)
			
	def on_text_motion_select(self, motion):
		if self.state == "setup" and self.boardtxt.focus:
			self.boardtxt.caret.on_text_motion_select(motion)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.ESCAPE:
			self._quit()
		if symbol == key.RETURN:
			self.set_fullscreen(self.fullscreen^True)
			self.update_coordinates()
		if symbol == key.C and modifiers and key.MOD_SHIFT:
			self.dispatch_event('on_reqconnect')
			self.msg = "Waiting for second player..."
		if symbol == key.E and key.MOD_SHIFT: 	# Конец игры
			self.state = "finish"
		if symbol == key.Q and key.MOD_SHIFT: 	# Для аутизм-режима
			self.player = self.player * 2%3
		if symbol == key.T and key.MOD_SHIFT:	# Для тестов. 
			#pyglet.clock.schedule_interval(lambda x: self.dispatch_event('on_key_press',key.G,False), 1/37)
#			self.stones[randint(0,self.BRD_H**2)].image = tiles[randint(0,4)]
#			print("Pomenyal prozrachnost' sluchaynogo sprite'a")
#			self.stones = np.transpose(self.stones)
			self.stones = np.flipud(np.rot90(self.stones))
			print(self.pulse_stone)
			pass

Board.register_event_type('on_mademove')
Board.register_event_type('on_movereceive')
Board.register_event_type('on_reqconnect')
Board.register_event_type('on_disconnect')

"""
Подобное будет в коде ланчера для добавления event_handler'а на событие хода:
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
	window = Board(BOARD_W, BOARD_H, WINDOW_W, WINDOW_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT)
	pyglet.clock.schedule_interval(lambda _: None, 1/150)
	keystate = key.KeyStateHandler()
	window.push_handlers(keystate)
	pyglet.app.run()