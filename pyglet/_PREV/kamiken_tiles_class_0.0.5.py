# -*- coding: UTF-8 -*-
'''
Kamiken tiles v0.0.5
To do:
fade_tile плохо отображается на последней (верхней) вертикали и горизонтали



'''

import pyglet
import numpy as np
import random
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
             'red'    : (255, 0, 0, 0.3),
             'blue'   : (0, 0, 255, 0.3),
             'board'  : (0.59, 0.54, 0.51, 0.3),
             'r_stone': (243, 104, 18, 255),
             'b_stone': (14, 193, 225, 255)      }

'''
Переменные 
'''
BOARD_W = 10
BOARD_H = 10
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

'''
Поле
'''
ALL_STONES = np.zeros([BOARD_W, BOARD_H])


for i in range(BOARD_W):
    for j in range(BOARD_H):
        ALL_STONES[i,j] = random.randint(0,5)

#ALL_STONES = np.eye(BOARD_W)

#ALL_STONES[0][0] = 1
#ALL_STONES[0][3] = 2
#ALL_STONES[3][1] = 3
#print(ALL_STONES)

'''
ALL_STONES = np.transpose(ALL_STONES)
ALL_STONES = np.fliplr(ALL_STONES)    
'''
'''    
print(ALL_STONES)
for i in range(BOARD_W):
    for j in range(BOARD_H):
        print('i, j = ', i, j)
        print('ALL_STONES[i][j]', ALL_STONES[i][j])
'''        

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
        self.fade_stone = pyglet.sprite.Sprite(tiles[PLAYER],
                                                     -1, -1,
                                                     batch = self.batch    )
        self.fade_stone.opacity = FADE_STONE_OPACITY
        self.zeros = []
        self.fps_display = pyglet.clock.ClockDisplay()
 
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
                if ALL_STONES[i-1,j-1] == 5.0:
                    new_stone = pyglet.sprite.Sprite(b_point, x_stone, y_stone,
                                                     batch = self.batch             )
                    new_stone1 = pyglet.sprite.Sprite(r_point, x_stone, y_stone,
                                                      batch = self.batch            )
                else:
                    new_stone = pyglet.sprite.Sprite(tiles[ALL_STONES[i-1,j-1]],
                                                     x_stone, y_stone,
                                                     batch = self.batch             )
                if ALL_STONES[i-1,j-1] == 0.0:
                    new_stone.opacity = BOARD_OPACITY
                    self.zeros.append((i, j))
                if new_stone1:
                    stones.append(new_stone1)
                if new_stone:
                    stones.append(new_stone)
        #print(self.zeros)
        self.batch.draw() 
        self.fps_display.draw()



    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            x -= 10
            y -= 20
            x1 = x//TILE_SIZE - 1
            y1 = y//TILE_SIZE - 1
            if 0 <= y1 <= BOARD_H - 1 and 0 <= x1 <= BOARD_W - 1:
                print('BOARD_H - 1, BOARD_W - 1: ', BOARD_H - 1, BOARD_W - 1)
                print('x1, y1 = ', x1, y1)
              #pass
              
    def on_mouse_motion(self, x, y, dx, dy):
        if (TILE_SIZE <= x <= WINDOW_W-2*TILE_SIZE) and (TILE_SIZE <= y <=
                                                       WINDOW_H-2*TILE_SIZE):
            x1 = (x+1)//TILE_SIZE - 1 
            y1 = (y+1)//TILE_SIZE - 1
            if (x1, y1) in self.zeros:
                self.fade_stone.x = (x1+1) * TILE_SIZE
                self.fade_stone.y = (y1+1) * TILE_SIZE
                self.clear()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            window.close()
        if symbol == key.RETURN:
            window.set_fullscreen(True)
 

window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
               FONT, ALL_STONES, PLAYER)

pyglet.app.run()



