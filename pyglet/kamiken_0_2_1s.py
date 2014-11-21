#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
#  - * -  coding: UTF - 8  - * - 
'''
Kamiken v0.2.0
'''

import pyglet
import sys
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from numpy import zeros, where
from random import randint
from configparser import ConfigParser

config = ConfigParser()
config.readfp(open("config021.ini"))

colors = {	'white'  : (255, 255, 255, 0.3),
	     	'red'    : (255, 0, 0, 0.3),
	     	'blue'   : (0, 0, 255, 0.3),
	     	'board'  : (0.59, 0.54, 0.51, 0.3),
	     	'r_stone': (243, 104, 18, 255),
	     	'b_stone': (14, 193, 225, 255),
	     	'text'	 : (14, 193, 225, 255)}

'''
Переменные
'''
BOARD_W = int(config.get('settings','board_size_w'))
BOARD_H = int(config.get('settings','board_size_h'))
MSG = 'KAMI~!!'
TILE_SIZE = 24
SQUARE_SIZE = 30
FONT = 'Comic Sans MS'
WINDOW_W = BOARD_W * TILE_SIZE + 2 * TILE_SIZE
WINDOW_H = BOARD_H * TILE_SIZE + 2 * TILE_SIZE
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
#r_point = pyglet.resource.image( config.get('images','red_point')	)
#b_point = pyglet.resource.image( config.get('images','blue_point')	)

board.anchor_x, board.anchor_y = board.width//2, board.height//2
r_stone.anchor_x, r_stone.anchor_y =r_stone.width//2, r_stone.height//2
b_stone.anchor_x, b_stone.anchor_y = b_stone.width//2, b_stone.height//2
r_board.anchor_x, r_board.anchor_y =r_board.width//2, r_board.height//2
b_board.anchor_x, b_board.anchor_y = b_board.width//2, b_board.height//2

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
            					dict(color=colors['text'],font_size=20))
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

class Board(pyglet.window.Window):

	def __init__(self, BOARD_W, BOARD_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT):
			# Изначальные игровые параметры
		self.player = 1
		self.turn = 1
		self.TILE_SIZE = TILE_SIZE
		self.SQUARE_SIZE = SQUARE_SIZE
		self.BRD_H = BOARD_H
		self.BRD_W = BOARD_W
		self.scale = self.TILE_SIZE/150
		self.state = "setup" # после коннекта на playing изменяется
			# окно и отступы
		self.WIN_W = (self.BRD_W+2)*self.SQUARE_SIZE
		self.WIN_H = (self.BRD_H+2)*self.SQUARE_SIZE
		super(Board, self).__init__(width=self.WIN_W, height=self.WIN_H, caption=('Kamiken'))
		self.set_fullscreen(eval(config.get('settings','fullscreen')))
		self.margin_v = (self.height - self.SQUARE_SIZE * self.BRD_H) // 2
		self.margin_h = (self.width - self.SQUARE_SIZE * self.BRD_W) // 2
			# графические параметры
		texture_set_mag_filter_nearest( r_stone.get_texture() )
		texture_set_mag_filter_nearest( b_stone.get_texture() )
		self.batch_launcher = pyglet.graphics.Batch()
		self.batch = pyglet.graphics.Batch()
		self.batch_fade = pyglet.graphics.Batch()
		self.FADE_X = 0
		self.FADE_Y = 0
		self.FADE_FLAG = False
		self.fps_display = pyglet.clock.ClockDisplay()
			# лейблы / текст
		self.msg = MSG
		self.label = pyglet.text.Label(
			text=self.msg, font_size=TILE_SIZE - 10, anchor_x='center', font_name=FONT,
			color=colors['b_stone'], x=self.width//2, y=self.height - 25,
			batch = self.batch)
		self.brdlabel = pyglet.text.Label(
			"Board size", font_size=15, anchor_x="center", font_name=FONT,
			color=colors['text'], x=self.width/2 - 40, y=self.height/2 + 50, 
			batch = self.batch)
		self.boardtxt = TextWidget(str(BOARD_H), self.width//2 + 60, self.height//2 + 41, 
									50, self.batch)
	
	def update_coordinates(self):
		"""
		Подбирает размер окна под размер поля; изменяет отступы, если размер окна
		изменился, чтобы поле осталось в центре. Если оконный режим — меняет размер окна.
		"""
		self.WIN_W = (self.BRD_W + 2) * self.SQUARE_SIZE
		self.WIN_H = (self.BRD_H + 2) * self.SQUARE_SIZE
		if not self.fullscreen:
			self.width=self.WIN_W
			self.height=self.WIN_H
		self.margin_v = (self.height - self.SQUARE_SIZE*self.BRD_H) // 2
		self.margin_h = (self.width - self.SQUARE_SIZE*self.BRD_W) // 2
		self.labels_redraw()

	def start_game(self):
		"""
		Из __init__ было сюда перенесено, чтобы изменить окно/доску после выбора в меню.
		Снова вернулись к квадратной. Из TextWidget'а берётся введённое число, 
		а дальше всё как и раньше.
		Снова вызывается функция обновления размера окна, отступов, координат лейблов.
		"""
		boardsize = int(self.boardtxt.document.text)
		self.boardtxt.layout.delete()
		self.brdlabel.delete()
		del self.boardtxt
		del self.brdlabel
		self.BRD_H = boardsize
		self.BRD_W = boardsize
		self.update_coordinates()
		self.ALL_STONES = zeros([self.BRD_W, self.BRD_H])
		self.dispatch_event('on_reqconnect')
		self.state = "playing"

	def labels_redraw(self):
		"""
		Проверяет, какие из лейблов/полей текста присутствуют (два из них удаляются
		после начала игры) и ставит на нужное место при изменении размера окна
		или перехода в полноэкранный режим.
		"""
		if hasattr(self, 'label'):
			self.label.x = self.width//2
			self.label.y = self.height - 25
		if hasattr(self, 'boardtxt'):
			self.boardtxt.layout.x = self.width//2 + 60
			self.boardtxt.layout.y = self.height//2 + 41
		if hasattr(self, 'brdlabel'):
			self.brdlabel.x = self.width/2 - 40
			self.brdlabel.y = self.height/2 + 50
		pass

	def on_draw(self):
		"""
		Фоновая картина и лейбл рисуются всегда. Дальше, в зависимости от состояния,
		будет вызываться либо функция прорисовки игры, либо функция прорисовки меню,
		либо конец игры и вывод счёта. 		
		"""
		self.clear()
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
		pyglet.gl.glClearColor( * colors['white'])
		stones = []
		self.fade_stone = pyglet.sprite.Sprite(tiles[self.turn],
						       self.FADE_X, self.FADE_Y,
						       batch = self.batch_fade)
		self.fade_stone.opacity = FADE_STONE_OPACITY
		for i in range(self.BRD_H):
			for j in range(self.BRD_W):
				x_stone = (i + 0.5) * self.SQUARE_SIZE + self.margin_h
				y_stone = (j + 0.5) * self.SQUARE_SIZE + self.margin_v
				if self.ALL_STONES[j,i] < 5.0:
					new_stone = pyglet.sprite.Sprite(tiles[self.ALL_STONES[j,i]],
									 x_stone, y_stone,
									 batch=self.batch         )
					new_stone.opacity = opacity[self.ALL_STONES[j,i]]
					stones.append(new_stone)
		self.batch.draw()
		if self.FADE_FLAG:
			self.batch_fade.draw()

	def draw_setup(self):
		xp1 = self.width//2 - self.TILE_SIZE * 3
		yp1 = self.height//2.5
		xp2 = self.width//2 + self.TILE_SIZE * 3
		yp2 = self.height//2.5
		pl1 = pyglet.sprite.Sprite(tiles[abs(self.player - 2)], xp1, yp1, batch=self.batch)
		pl2 = pyglet.sprite.Sprite(tiles[self.player * 2 - 2], xp2, yp2, batch=self.batch)
		pl1.scale = 3; pl2.scale = 3
		if abs(self.player - 2) == 1: pl2.opacity = 50
		else: pl1.opacity = 50
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
		self.label_update()

	def on_movereceive(event,self,player,x,y):
		"""
		'self' стоит не первым из - за того, что событие вызывается извне и сам класс
		доски вообще в явном виде передаётся при создании события.
		"""
		if player==0:
			self.label_update()
		self.make_move(x,y,player)

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
			
			if xp1 <= x <= xp1 + self.TILE_SIZE * 3 and yp1 <= y <= yp1 + self.TILE_SIZE * 3 \
				or xp2 <= x <= xp2 + self.TILE_SIZE * 3 and yp2 <= y <= yp2 + self.TILE_SIZE * 3:
					self.start_game()
					self.msg = "Waiting for second player..."
# 			elif xp2 <= x <= xp2 + self.TILE_SIZE * 3 and yp2 <= y <= yp2 + self.TILE_SIZE * 3:
# 				self.start_game()
# 				self.msg = "Waiting for second player..."
			
		elif button == mouse.LEFT and self.state == "playing":
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
		if self.state == "setup":
			xp1 = self.width//2 - self.TILE_SIZE * 4.5
			yp1 = self.height//2.5 - self.TILE_SIZE * 1.5
			xp2 = self.width//2 + self.TILE_SIZE * 1.5
			yp2 = self.height//2.5 - self.TILE_SIZE * 1.5
			if xp1 <= x <= xp1 + self.TILE_SIZE * 3 and yp1 <= y <= yp1 + self.TILE_SIZE * 3:
				self.player = 1
			if xp2 <= x <= xp2 + self.TILE_SIZE * 3 and yp2 <= y <= yp2 + self.TILE_SIZE * 3:
				self.player = 2
	
		elif (self.margin_h <= x < self.width - self.margin_h) and (self.margin_v <= y <
				self.height - self.margin_v) and self.state == "playing":
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
		self.clear()
	
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
		if symbol == key.E and key.MOD_SHIFT: 	# Для аутизм - режима
			self.state = "finish"
		if symbol == key.Q and key.MOD_SHIFT: 	# Для аутизм - режима
			self.player = self.player * 2%3
		if symbol == key.T and key.MOD_SHIFT:	# тесты - хуесты. 
			pass
#			self.margin_h-=5
			
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
	window = Board(BOARD_W, BOARD_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT)

	pyglet.app.run()
