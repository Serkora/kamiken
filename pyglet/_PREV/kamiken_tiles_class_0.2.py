# -*- coding: UTF-8 -*-
'''
Kamiken tiles v0.0.2




'''

import pyglet
import numpy as np
import random
from pyglet.window import mouse, key

'''
Переменные 
'''
BOARD_W = 10
BOARD_H = 10
MSG = 'KAMI~!!'
TILE_SIZE = 30 
FONT = 'Comic Sans MS'

'''
Изображения
'''
r_stone = pyglet.resource.image('r_stone.png')
b_stone = pyglet.resource.image('b_stone.png')
r_point = pyglet.resource.image('r_point.png')
b_point = pyglet.resource.image('b_point.png')
board = pyglet.resource.image('board.png')

'''
Поле
'''
ALL_STONES = np.zeros([BOARD_W, BOARD_H])
for i in range(BOARD_W):
    for j in range(BOARD_H):
        ALL_STONES[i,j] = random.randint(0,5)
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
             'b_stone': (14, 193, 225, 255)          }

tiles = {    1.0        : r_stone,
             2.0        : b_stone,
             3.0        : r_point,
             4.0        : b_point                      }



class Board(pyglet.window.Window):

    def __init__(self, BOARD_W, BOARD_H, MSG, TILE_SIZE, FONT, ALL_STONES):
        super(Board, self).__init__(width=BOARD_W*TILE_SIZE,
                                    height=BOARD_H*TILE_SIZE + TILE_SIZE,
                                    caption='Kamiken'                    )
        self.batch = pyglet.graphics.Batch()
        self.label = pyglet.text.Label(text=MSG, font_size=BOARD_W*2,
                                       font_name=FONT,
                                       color=colors['b_stone'],
                                       x = 0, y =BOARD_H*TILE_SIZE+5,
                                       batch = self.batch                     )
        self.BOARD_W = BOARD_W
        self.BOARD_H = BOARD_H
        self.MSG = MSG
        self.TILE_SIZE = TILE_SIZE
        self.FONT = FONT
        self.ALL_STONES = ALL_STONES
     


    
    def on_draw(self):
        pyglet.gl.glClearColor(*colors['board'])
        window.clear()
        stones = []
        for i in range(BOARD_H+1):
            for j in range(BOARD_W+1):
                new_stone1 = False
                new_stone = False
                x_stone = i*TILE_SIZE-TILE_SIZE
                y_stone = j*TILE_SIZE-TILE_SIZE
                board.blit(x_stone,y_stone)
                if ALL_STONES[i-1,j-1] == 5.0:
                    new_stone = pyglet.sprite.Sprite(b_point, x_stone, y_stone,
                                                     batch = self.batch             )
                    new_stone1 = pyglet.sprite.Sprite(r_point, x_stone, y_stone,
                                                      batch = self.batch            )
                elif ALL_STONES[i-1,j-1] != 0.0:
                    new_stone = pyglet.sprite.Sprite(tiles[ALL_STONES[i-1,j-1]],
                                                     x_stone, y_stone,
                                                     batch = self.batch             )
                if new_stone1:
                    stones.append(new_stone1)
                if new_stone:
                    stones.append(new_stone)
        self.batch.draw() 



    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            x1 = x//TILE_SIZE
            y1 = y//TILE_SIZE
            if y1 <= BOARD_H - 1 and x1 <= BOARD_W - 1:
                print( x1, y1)
                

        

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            window.close()
        if symbol == key.RETURN:
            window.set_fullscreen(True)



window = Board(BOARD_W, BOARD_H, MSG, TILE_SIZE, FONT, ALL_STONES)

pyglet.app.run()



