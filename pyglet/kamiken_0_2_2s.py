#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
#  - * -  coding: UTF - 8  - * - 
'''
Kamiken v0.2.1
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
WINDOW_W = int(config.get('settings', 'window_width'))
WINDOW_H = int(config.get('settings', 'window_height'))
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
#r_point = pyglet.resource.image( config.get('images','red_point')	)
#b_point = pyglet.resource.image( config.get('images','blue_point')	)

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

		self.skipturn = pyglet.text.Label(
			"Skip turn", anchor_x="left", anchor_y = "top", 
			font_name=FONT, color=colors['textb'], batch = self.batch)
		self.endgame = pyglet.text.Label(
			"Finish game", anchor_x="left", anchor_y = "top", 
			font_name=FONT, color=colors['textb'], batch = self.batch)
		self.settings = pyglet.text.Label(
			"Settings", anchor_x="left", anchor_y = "top", 
			font_name=FONT, color=colors['textb'], batch = self.batch)
		self.disconnect = pyglet.text.Label(
			"Disconnect", anchor_x="left", anchor_y = "top", 
			font_name=FONT, color=colors['textb'], batch = self.batch)
		self.quitbt = pyglet.text.Label(
			"Quit", anchor_x="left", anchor_y = "top", 
			font_name=FONT, color=colors['textb'], batch = self.batch)

		
		self.buttons = [self.skipturn, self.endgame, self.settings, 
						self.disconnect, self.quitbt]
		
		self.place_buttons()
	
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
		for button in self.buttons:
			if button.x <= x <= button.x + button.content_width and \
				button.y - button.content_height <= y <= button.y:
					button.color = colors['textr']
			else:
				button.color = colors['textb']
	
	def button_press(self, x, y):
		for button in self.buttons:
			if button.x <= x <= button.x + button.content_width and \
				button.y - button.content_height <= y <= button.y:
					button.color = (0,255,0,255)

class Board(pyglet.window.Window):

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
		self.pulseiter = 0
			# окно и отступы
		self.WIN_W = WINDOW_W
		self.WIN_H = WINDOW_H
		super(Board, self).__init__(width=self.WIN_W, height=self.WIN_H, 
									caption=('Kamiken'), vsync=True)
		self.set_fullscreen(eval(config.get('settings','fullscreen')))
		self.margin_v = (self.height - self.SQUARE_SIZE * self.BRD_H) // 2
		self.margin_h = (self.width - self.SQUARE_SIZE * self.BRD_W) // 4
			# графические параметры
		self.batch_launcher = pyglet.graphics.Batch()
		self.batch_menu = pyglet.graphics.Batch()
		self.batch = pyglet.graphics.Batch()
		self.batch_fade = pyglet.graphics.Batch()
		self.FADE_X = 0
		self.FADE_Y = 0
		self.FADE_FLAG = False
		self.pulseopacity = 1
		self.pulse_stone = (-1,-1)
		self.fps_display = pyglet.clock.ClockDisplay()
			# лейблы / текст
		self.msg = MSG
		self.label = pyglet.text.Label(
			text=self.msg, font_size=TILE_SIZE - 10, anchor_x='center', font_name=FONT,
			color=colors['b_stone'], x=self.width//2, y=self.height - 25,
			batch = self.batch)
		self.startuplabels()

	
	def startuplabels(self):
		"""
		Создаёт лейблы/виджеты настроек.
		"""
		self.brdlabel = pyglet.text.Label(
			"Board size", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['textb'], x=self.width/2 - 40, y=self.height/1.35, 
			batch = self.batch)
		self.boardtxt = TextWidget(str(BOARD_H), self.width/2 + 60, self.height/1.35 - 7.5, 
										50, self.batch)
		self.sp_label = pyglet.text.Label(
			"Single Player", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['textb'], x=self.width/2-70, y=self.height/1.6, 
			batch = self.batch)
		self.mp_label = pyglet.text.Label(
			"Multiplayer", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['textb'], x=self.width/2+70, y=self.height/1.6, 
			batch = self.batch)
		
	def update_coordinates(self):
		"""
		Подбирает размер окна под размер поля; изменяет отступы, если размер окна
		изменился, чтобы поле осталось в центре. Если оконный режим — меняет размер окна.
		Также меню присваиватся новые координаты, и обновляется расположение кнопок.
		"""
		self.SQUARE_SIZE = (self.height - 60)//self.BRD_H
		self.TILE_SIZE = 0.8 * self.SQUARE_SIZE
		self.scale = self.TILE_SIZE/150
		self.margin_v = (self.height - self.SQUARE_SIZE*self.BRD_H) // 2
		self.margin_h = (self.width - self.SQUARE_SIZE*self.BRD_W) // 4
		self.labels_redraw()
		self.game_menu.place_buttons()
		self.FADE_FLAG = False # скорее всего, курсор будет уже на другом местеЙ

	def start_game(self):
		"""
		Из __init__ было сюда перенесено, чтобы изменить окно/доску после выбора в меню.
		Снова вернулись к квадратной. Из TextWidget'а берётся введённое число, 
		а дальше всё как и раньше.
		Снова вызывается функция обновления размера окна, отступов, координат лейблов.
		В стек добавляется функция, изименяющая прозрачность последнего хода каждые 1/30с.
		В принципе, туда можно добавить и другую анимацию.
		menu_def_x/y вынесены для удобности редактирования/восприятия.
		Используется lambda для того, чтобы menu.x (отправная точна координат отедльных
		кнопок) было функцией, меняющей значение в зависимости от размеров окна 
		без эксплицитного объявления этого изменения.
		"""
		boardsize = int(self.boardtxt.document.text)
		self.boardtxt.layout.delete()
		self.brdlabel.delete()
		self.sp_label.delete()
		self.mp_label.delete()
		del self.boardtxt
		del self.brdlabel
# 		del self.sp_label
# 		del self.mp_label
		self.BRD_H = boardsize
		self.BRD_W = boardsize
		menu_def_x = lambda: self.margin_h + (self.BRD_H+0.5) * self.SQUARE_SIZE
		menu_def_y = lambda: self.height - self.margin_v
		self.game_menu = GameMenu(menu_def_x, menu_def_y, height=lambda: self.height,
									board=self, batch=self.batch_menu,
									orientation = "vertical")
		self.update_coordinates()
		self.ALL_STONES = zeros([self.BRD_W, self.BRD_H])
		self.dispatch_event('on_reqconnect')
		self.state = "playing"
		pyglet.clock.schedule_interval(self.pulsation,1/30)

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
		if hasattr(self, 'skipturn_label'):
			self.skipturn_label.x = self.margin_h
			self.skipturn_label.y = self.margin_v/2
		if hasattr(self, 'endgame_label'):
			self.endgame_label.x = self.margin_h + 70
			self.endgame_label.y = self.margin_v/2
		if hasattr(self, 'settings_label'):
			self.settings_label.x = self.margin_h + 150
			self.settings_label.y = self.margin_v/2
		if hasattr(self, 'disconnect_label'):
			self.disconnect_label.x= self.margin_h + 220
			self.disconnect_label.y = self.margin_v/2
		pass
	
	def pulsation(self,trash):
		self.pulseopacity = 200+55*cos(self.pulseiter)
		self.pulseiter = (self.pulseiter+pi/10)%(2*pi)

	
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
#		self.fps_display.draw()
		
		if self.state=="playing": self.draw_game()
		elif self.state=="setup": self.draw_setup()	
		elif self.state=="finish": self.draw_finish()
	
	def draw_game(self):
		"""
		Начало поля начинается с конца отступов self.margin_h/v
		Так как прозрачные области были из спрайтов камней убраны, каждый камень
		рисуется с дополнительным отступом: разницей между размером спрайта и необходимым
		размером одной клетки.
		(i+0.5) и (j+0.5) нужны потому что anchor спрайтов в центре, а не нижнем углу.
		"""
		stones = []
		self.fade_stone = pyglet.sprite.Sprite(tiles[self.turn],
						       self.FADE_X, self.FADE_Y,
						       batch = self.batch_fade)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		self.fade_stone.scale = self.scale
		for i in range(self.BRD_H):
			for j in range(self.BRD_W):
				x_stone = (i + 0.5) * self.SQUARE_SIZE + self.margin_h
				y_stone = (j + 0.5) * self.SQUARE_SIZE + self.margin_v
				if self.ALL_STONES[j,i] < 5.0:
					new_stone = pyglet.sprite.Sprite(tiles[self.ALL_STONES[j,i]],
									 x_stone, y_stone,
									 batch=self.batch         )
					new_stone.scale = self.scale
					if (i,j) == self.pulse_stone:
						new_stone.opacity = self.pulseopacity
					else:
						new_stone.opacity = opacity[self.ALL_STONES[j,i]]
					stones.append(new_stone)
		self.batch.draw()
		self.batch_menu.draw()
		if self.FADE_FLAG:
			self.batch_fade.draw()

	def draw_setup(self):
		xp1 = self.width//2 - self.TILE_SIZE * 3
		yp1 = self.height//2.5
		xp2 = self.width//2 + self.TILE_SIZE * 3
		yp2 = self.height//2.5
		pl1 = pyglet.sprite.Sprite(tiles[abs(self.player - 2)], xp1, yp1, batch=self.batch)
		pl2 = pyglet.sprite.Sprite(tiles[self.player * 2 - 2], xp2, yp2, batch=self.batch)
		pl1.scale = self.scale * 3; pl2.scale = self.scale * 3
		if abs(self.player - 2) == 1: pl2.opacity = 50
		else: pl1.opacity = 50

		if self.gametype == "multiplayer": 
			mp_sel = pyglet.sprite.Sprite(mp_select, self.mp_label.x, self.mp_label.y,
											batch=self.batch)
		else:
			sp_sel = pyglet.sprite.Sprite(sp_select, self.sp_label.x, self.sp_label.y,
											batch=self.batch)
		self.batch.draw()
		pass

	def draw_finish(self):
		self.draw_game()
		score_r = len(where(self.ALL_STONES==3)[0])
		score_b = len(where(self.ALL_STONES==4)[1])
		self.msg = "Red: "+str(score_r)+"  Blue: "+str(score_b)

	def make_move(self,x1,y1,pl):
		"""
		Проверяет, действитеьно ли сейчас ход того игрока, кем была вызвана функция,
		или есть ли уже камень на том месте, на которое кликнули — если да, то
		возвращает из функции. Проверка полезна из-за дублирования передаваемых и 
		получаемых клиентом сообщений.
		Смотрит 4 клетки вокруг той, на которую кликнули, и меняет их значения 
		соответственно правилам.
		"""
		if self.turn != pl or self.ALL_STONES[y1,x1] == pl:	return
		self.ALL_STONES[y1,x1] = pl
		for i in range(-1,2):
			for j in range(-1,2):
				if abs(i - j) == 1:
					try:
						if self.ALL_STONES[abs(y1 + i),abs(x1 + j)] != pl:
							x = self.ALL_STONES[abs(y1 + i),abs(x1 + j)];
							self.ALL_STONES[abs(y1 + i),abs(x1 + j)] = tilehits[pl,x]
					except: pass
		self.turn = self.turn * 2%3  # 1 - >2, 2 - >1
		self.FADE_FLAG = False
		self.pulse_stone = (x1,y1)
		self.label_update()

	def on_movereceive(event,self,player,x,y):
		"""
		'self' стоит не первым из - за того, что событие вызывается извне и сам класс
		доски вообще в явном виде передаётся при создании события.
		"""
		if player==0:
			self.label_update()
		self.make_move(x,y,player)

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
		if (self.margin_h <= x < self.width - self.margin_h) and (self.margin_v <= y <
				self.height - self.margin_v):
			x1 = (x - self.margin_h)//self.SQUARE_SIZE
			y1 = (y - self.margin_v)//self.SQUARE_SIZE
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
		
	def on_mouse_press(self, x, y, button, modifiers):
		"""
		Если клик был по полю для ввода размера доски, то появляется каретка и
		можно изменять текст. Если вне — каретка пропадает, писать нельзя.
		Если был клик по любому из камней выбора игрока, начинается игра (номер игрока
		уже выбран при наведении курсора на камень), запускаются функции изменения 
		размера доски, окна и т.д.
		При ходе создаётся событие, которе при наличии сетевого клиента перехватывается
		и высылает ход на сервер. Повторяется 5 раз с интервалом в 100мс.
		Если клиента нет, то ничего не происходит.
		"""
		if button == mouse.LEFT and self.state == "setup":
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
				
		elif button == mouse.LEFT and self.state == "playing":
			self.game_menu.button_press(x,y)
			x1 = (x - self.margin_h)//self.SQUARE_SIZE
			y1 = (y - self.margin_v)//self.SQUARE_SIZE
			if 0 <= y1 < self.BRD_H and 0 <= x1 < self.BRD_W:
				if self.ALL_STONES[y1,x1]%(self.player + 2) == 0 and self.turn == self.player:
					self.make_move(x1,y1,self.player)
					for i in range(0,5):
						pyglet.clock.schedule_once(
						lambda x: self.dispatch_event('on_mademove',self.player,x1,y1), (i*0.1)
						)

	def on_mouse_motion(self, x, y, dx, dy):
		"""
		Чтобы не забивать это обработчик событий кучей условий (а их будет много), 
		присвоений и прочей фигни, решил вынести всё в отедльные функции, а тут
		только вызывать то, что нужно, в зависимсоти от состояния игры.
		"""
		self.msg = str(x)+"  "+str(y)
		if self.state == "playing":
# 			self.mouse_motion_play(x,y)
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
			self.close()
		if symbol == key.RETURN:
			self.set_fullscreen(self.fullscreen^True)
			self.update_coordinates()
		if symbol == key.C and modifiers and key.MOD_SHIFT:
			self.dispatch_event('on_reqconnect')
			self.msg = "Waiting for second player..."
		if symbol == key.E and key.MOD_SHIFT: 	# Конец игры
			self.state = "finish"
		if symbol == key.Q and key.MOD_SHIFT: 	# Для аутизм - режима
			self.player = self.player * 2%3
		if symbol == key.T and key.MOD_SHIFT:	# Для тестов. 
			pass
						
	def label_update(self):
		if self.turn==self.player:
			self.msg = 'Your turn!'
		else:
			self.msg = "Opponent's turn!"
	


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
def texture_set_mag_filter_nearest( texture ): #функция, преобразующая изображение в текстуру OpenGL со всякими фильтрами
	glBindTexture( texture.target, texture.id  )
	glTexParameteri( texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
	glBindTexture( texture.target, 0 )		

if __name__ == "__main__":
	window = Board(BOARD_W, BOARD_H, WINDOW_W, WINDOW_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT)
	pyglet.clock.schedule(lambda x: None)
	pyglet.app.run()
