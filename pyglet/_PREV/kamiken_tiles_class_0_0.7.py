# -*- coding: UTF-8 -*-
'''
Kamiken tiles v0.0.7-1
To do:
после ход полупрозрачный камень рисуется поверх уже поставленного



'''

import pyglet
import numpy as np
import random
from pyglet.window import mouse 
from pyglet.window import key
import time

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
             'red'    : (255, 0, 0, 0.3),
             'blue'   : (0, 0, 255, 0.3),
             'board'  : (0.59, 0.54, 0.51, 0.3),
             'r_stone': (243, 104, 18, 255),
             'b_stone': (14, 193, 225, 255)      }

'''
Переменные 
'''
BOARD_W = 13
BOARD_H = 13
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
image   = pyglet.resource.image( 'image5.png'    )
r_stone = pyglet.resource.image( 'r_stone.png'   )
b_stone = pyglet.resource.image( 'b_stone.png'   )
r_point = pyglet.resource.image( 'r_point_2.png' )
b_point = pyglet.resource.image( 'b_point_2.png' )
board   = pyglet.resource.image( 'board_7.png'   )

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

'''
Поле
'''
ALL_STONES = np.zeros([BOARD_W, BOARD_H])

class Board(pyglet.window.Window):

    def __init__(self, WINDOW_W, WINDOW_H, BOARD_W, BOARD_H,
                 MSG, TILE_SIZE, FONT, ALL_STONES, PLAYER             ):
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
        '''
Значит так. В функции инициализации класса мы объявляем только неизменные 
параметры - то есть те, которые должны быть у объекта, когда мы его
создаем. Чуть выше мы создаем два "батча" - контейнера для графики. 
Batch - для всего что мы рисовали до
этого и batch_fade исключительно для полупрозрачных камней. self.turn - 
вообще изначально я предпологал что он НИ НУЖЕН, так как ход будет опре
деляться значением PLAYER (переменная будет меняться каждый ход, ведь они,
ходы, будут на разных машинах фактически), но для пробы чего уж там.
лейбл то же понятно, если мы хотим его сделать более гибким, следует 
перенести его объявление в другое место.
self.FADE_X/Y - это координаты полупрозрачного тайла. При создании окна мы
делаем их равными нулю. self.FADE_FLAG параметр говорящий, рисовать или не
рисовать полупрозрачный камень.
Теперь функция on_draw(). Как следует из названия, это НЕ функция рисования, 
это функция, в которую можно написать процедуры, которые будут происходить
при рисовании окна. Так же как и on_mouse_motion() это то что будет происходить
если двинуть мышку. Т.е. окно будет рисоваться в любом случае, а от того что
написано в on_draw() зависит что именно. Поэтому как то вызывать ее бессмысленно,
точно так же как нельзя дать ей какие то параметры, кроме самого объекта.
Поэтому мы создали несколько дополнительных параметров нашего окна, отвечающих
за рисование полупрозрачного камня. 
В функции движения мышки мы, в случае необходимости, присваиваем этим параметрам
нужные значения (если надо рисовать камень флаг делаем тру, и координатам присва
ваем координаты ловко вычисленные тобой). 
Ну а в функции on_draw(), ничего не поделаешь, приходится создать условие-
если флаг тру, тогда рисуем batch_fade. Кажеться, иначе сделать невозможно. 
        Правда вот смысла в этом нет - очевидно что просто  его в -50 -50 гораздо
        проще и экономнее. Но в принципе. Можно, например, по дефолту рисовать не в 0
        0, а  центре,  туда же курсор мышки ставить насильно. Ну кто его знает
        короче что понадобиться.
        '''
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
       # print('IMG_IN_WINDOW_W,H = ', IMG_IN_WINDOW_W, IMG_IN_WINDOW_H)
       # image.blit(x=self.width//2-image.width//2, y=self.height//2-image.height//2)
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
        if self.FADE_FLAG:
            self.batch_fade.draw()
            
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
                    self.FADE_FLAG = False #вот это интересно кстати. Если этого не сделать будет
                    #раздражающий баг, попробуй если хочешь. Но если я правильно понимаю при 
                    #игре на разных машинах этот параметр будет совсем по другому использоваться.
                
                
                
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
 

window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
               FONT, ALL_STONES, PLAYER)

						
pyglet.app.run()