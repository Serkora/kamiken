###/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-

import tkinter as tk
import numpy as np
import pyglet
import random
import time
from pyglet.window import mouse
from pyglet.window import key
from threading import Thread
from threading import active_count


colors = {   'white'  : (255, 255, 255, 0.3),
             'red'    : (255, 0, 0, 0.3),
             'blue'   : (0, 0, 255, 0.3),
             'board'  : (0.59, 0.54, 0.51, 0.3),
             'r_stone': (243, 104, 18, 255),
             'b_stone': (14, 193, 225, 255)      }

'''
Переменные 
'''
BOARD_W = 10
BOARD_H = 5
MSG = 'KAMI~!!'
TILE_SIZE = 30 
FONT = 'Comic Sans MS'
WINDOW_W = BOARD_W * TILE_SIZE + 2 * TILE_SIZE
WINDOW_H = BOARD_H * TILE_SIZE + 2 * TILE_SIZE
BOARD_OPACITY = 40 #opacity 0-255
FADE_STONE_OPACITY = 150
global PLAYER
PLAYER = 2.0 #1.0 - red, 2.0 - blue

'''
Изображения
'''
image   = pyglet.resource.image( 'pics/image5.png'    )
r_stone = pyglet.resource.image( 'pics/r_stone.png'   )
b_stone = pyglet.resource.image( 'pics/b_stone.png'   )
r_point = pyglet.resource.image( 'pics/r_point.png' )
b_point = pyglet.resource.image( 'pics/b_point.png' )
board   = pyglet.resource.image( 'pics/board_5.png'   )

tiles = {    0.0        : board,
             1.0        : r_stone,
             2.0        : b_stone,
             3.0        : r_point,
             4.0        : b_point                }
             
tilenames = {0.0        : 'board',
             1.0        : 'r_stone',
             2.0        : 'b_stone',			   	# Для вывода в консоль состояния 
             3.0        : 'r_point',   				# клетки при клике.
             4.0        : 'b_point', 
             5.0		: 'both'               }

ALL_STONES = np.zeros([BOARD_H, BOARD_W])  


class Board(pyglet.window.Window):

    def __init__(self, WINDOW_W, WINDOW_H, BOARD_W, BOARD_H,
                 MSG, TILE_SIZE, FONT, ALL_STONES, PLAYER             ):
        super(Board, self).__init__(width=WINDOW_W, height=WINDOW_H,
                                    caption='Kamiken')
        self.batch = pyglet.graphics.Batch()
        self.label = pyglet.text.Label(text=MSG, font_size=TILE_SIZE-10,
                                       anchor_x = 'center',
                                       font_name=FONT,
                                       color=colors['b_stone'],
                                       x = self.width//2,
                                       y = BOARD_H*TILE_SIZE+TILE_SIZE+5,
                                       batch = self.batch
                                       )
        '''
        Создаем полупрозрачный спрайт  по дефолту в 0 0
        '''
        # Поставил их в -50 -50, чтобы не было видно. Я не понимаю когда именно оно рисует,
        # как эти on_draw ивентом управлять и т.д., поэтому не могу сделать так, 
        # чтобы не рисовало сразу оба камня.
        self.fade_stone1 = pyglet.sprite.Sprite(tiles[1],
                                                     -50, -50,
                                                     batch = self.batch    )
        self.fade_stone2 = pyglet.sprite.Sprite(tiles[2],
                                                     -50, -50,
                                                     batch = self.batch    )
        self.fade_stone1.opacity = FADE_STONE_OPACITY
        self.fade_stone2.opacity = FADE_STONE_OPACITY
        self.fade_stones=[self.fade_stone1,self.fade_stone2]
        self.zeros = []
        self.fps_display = pyglet.clock.ClockDisplay()
        self.turn = PLAYER
 
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
       # print('IMG_IN_WINDOW_W,H = ', IMG_IN_WINDOW_W, IMG_IN_WINDOW_H)
       # image.blit(x=self.width//2-image.width//2, y=self.height//2-image.height//2)
        stones = []
        WINDOW_W_T = WINDOW_W // TILE_SIZE
        WINDOW_H_T = WINDOW_H // TILE_SIZE
        for i in range(BOARD_W):
            for j in range(BOARD_H):
                new_stone1 = False
                new_stone = False
                x_stone = i*TILE_SIZE+TILE_SIZE 
                y_stone = j*TILE_SIZE+TILE_SIZE
                #print('i, j= ', i, j)
                #print('ALL_STONES[i-1,j-1]= ', ALL_STONES[i-1,j-1] )
                '''
                Почему-то я тут поменял местами j и i. Я уже не помню, почему, но
                работает, лол.
                '''
                if ALL_STONES[j,i] == 5.0:
                    new_stone = pyglet.sprite.Sprite(b_point, x_stone, y_stone,
                                                     batch = self.batch             )
                    new_stone1 = pyglet.sprite.Sprite(r_point, x_stone, y_stone,
                                                      batch = self.batch            )
                else:
                    new_stone = pyglet.sprite.Sprite(tiles[ALL_STONES[j,i]],
                                                     x_stone, y_stone,
                                                     batch = self.batch             )
                if ALL_STONES[j,i] == 0.0:
                    new_stone.opacity = BOARD_OPACITY
                if new_stone1:	
                    stones.append(new_stone1)
                if new_stone:
                    stones.append(new_stone)                     
        self.batch.draw() 
#        self.fps_display.draw() 
  
    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            x1 = x//TILE_SIZE
            y1 = y//TILE_SIZE
            PLAYER = self.turn
            if 1 <= y1 <= BOARD_H and 1 <= x1 <= BOARD_W:
                if ALL_STONES[y1-1,x1-1]%(PLAYER+2)==0:
                    ALL_STONES[y1-1,x1-1]=PLAYER	# Координаты клеток начинаются с (1,1),
                    								# а индексы — с (0,0)
                    '''
                    Ебанутая операция присвоения клетке значения позволяет одинаковым
                    действием перейти от нуля к 3 или 4 в зависимости от игрока,
                    а также от 3 и 4 к 5, опять же в зависимости от игрока. Из 5 делает 5.
                    Парочка abs() нужна из-за восможности питона иметь отрицательные индексы,
                    уходя на противоположную сторону поля. А мы не в змейку тут играем.
                    Соответственно, пробует проверить все 4 клетки вокруг указанной.
                    '''	
                    try:
                    	if ALL_STONES[abs(y1-2),x1-1]!=PLAYER: 
 #                           print(round(ALL_STONES[abs(y1-2),x1-1]/((PLAYER-1)*6+1.5)))
                    	    x = ALL_STONES[abs(y1-2),x1-1]; pl = PLAYER
                    	    ALL_STONES[abs(y1-2),x1-1] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
                    except: pass
                    try: 
                       	if ALL_STONES[y1-1,abs(x1-2)]!=PLAYER:
                            x = ALL_STONES[y1-1,abs(x1-2)]; pl = PLAYER
                            ALL_STONES[y1-1,abs(x1-2)] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
                    except: pass
                    try: 
                        if ALL_STONES[y1,x1-1]!=PLAYER:
                            x = ALL_STONES[y1,x1-1]; pl = PLAYER
                            ALL_STONES[y1,x1-1] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
                    except: pass
                    try: 
                        if ALL_STONES[y1-1,x1]!=PLAYER:
                            x = ALL_STONES[y1-1,x1]; pl = PLAYER
                            ALL_STONES[y1-1,x1] = ((x*6)%29%(18+pl*3)%(19-pl)%2)*2/pl+pl+2
                    except: pass
                    self.turn = self.turn*2%3  # 1->2, 2->1
                
                
                
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
                self.fade_stones[PLAYER-1].x = (x1) * TILE_SIZE
                self.fade_stones[PLAYER-1].y = (y1) * TILE_SIZE
        self.clear()
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            pyglet.app.exit()
            menu.root.update()
            menu.root.deiconify()
        if symbol == key.RETURN:
            window.set_fullscreen(True)
 

# window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
#                FONT, ALL_STONES, PLAYER)



class Menu(object):
	def __init__(self, master):
		self.root = master
		self.root.wm_title("Kamiken menu")
		self.root.geometry('{}x{}'.format(500,300))
		self.root.configure(background='white')

		self.bt = tk.Button(master = self.root, text = 'continue', command = self.cont)
		self.bt.place(relx=0.5,rely=0.5,anchor='c')

		self.bt = tk.Button(master = self.root, text = 'kami', command = self.kami)
		self.bt.place(relx=0.2,rely=0.5,anchor='c')
		
		self.bt = tk.Button(master = self.root, text = 'exit', command = self._exit)
		self.bt.place(relx=0.8,rely=0.5,anchor='c')
		
	def kami(self):
		self.hide()
		runkami()
# 		ThrKami = Thread(target=runkami, args=())
# 		ThrKami.setDaemon(False)
# 		ThrKami.start()
		
		
	def hide(self):
		self.root.withdraw()
#		self.nw = tk.Toplevel()
		
# 		self.bt2 = tk.Button(master = self.nw, text = 'button', command = self.show)
# 		self.bt2.place(relx=0.5,rely=0.5,anchor='c')
	
	def cont(self):
		self.hide()
		pyglet.app.run()
	
	def show(self):
		self.nw.destroy()
		self.root.update()
		self.root.deiconify()
	
	def _exit(self):
		pyglet.app.exit()
		self.root.quit()
		
def menuopen():
	global menu
	menu = Menu(tk.Tk())
	tk.mainloop()

def runkami():
	global window
	window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
					FONT, ALL_STONES, PLAYER)	
	pyglet.app.run()
	
	
menuopen()