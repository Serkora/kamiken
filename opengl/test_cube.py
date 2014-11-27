#!/usr/bin/env python
#  - * -  coding: UTF - 8  - * - 



from math import pi, sin, cos, acos

import pyglet
from pyglet.gl import *

try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4, 
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)

@window.event
def on_resize(width, height):
    # Override the default on_resize handler to create a 3D projection
    '''
    определяем что то вроде поля зрения, часть плоскости с началом 
    в левом нижнем угле окна и концом в правом верхнем
    '''
    glViewport(0, 0, width, height) 
    glMatrixMode(GL_PROJECTION) #эта строчка говорит о том, что сейчас мы работаем
    #с матрицей "проекции"
    glLoadIdentity()#эта строчка как бы читает эту матрицу в буфер обмена или что
    #то подобное, ее надо вызыватьв сякий раз, как хочешь что-то сделать
    gluPerspective(60., width / float(height), .1, 1000.)#это устанавливает как
    #бы угол зрения что-ли
    glMatrixMode(GL_MODELVIEW)#теперь опять работаем с матрицей модельки
    return pyglet.event.EVENT_HANDLED
    '''
    Как будто в опенгле одна матрица для всего? 
    '''

def update(dt):
    '''
    Тут все понятно — вычисляем приращения координат, но возвращает функция в 
    глобальное пространство и не сами координаты, а остаток их деления на 360.
    '''
    global rx, ry, rz
    rx += dt * 1
    ry += dt * 80
    rz += dt * 30
    rx %= 360
    ry %= 360
    rz %= 360
pyglet.clock.schedule(update)

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #это очищает так называемые 
    #буферы, в первом хранится информация о цвете, а во втором непонятно о чем,
    #но он очевидно связан с "глубиной".
    glLoadIdentity()
    glTranslatef(0, 0, -20)#эта функция двигает "камеру". Сейчас она двигается 
    #"вверх", в сторону зрителя. Можно двигать относительно модели, можно 
    #относительно "перспективы" (туманная фраза, но суть в том, что движение
    #происходит в зависимости от текущей матрицы)
    glRotatef(rz, 0, 0, 1)#встроенная функция поворота, первый аргумент говорит
    glRotatef(ry, 0, 1, 0)#на сколько градусов (м.б. отрицательным), остальные
    glRotatef(rx, 1, 0, 0)#в формате True/False по какой оси (x,y,z соответственно)
    batch.draw()

def setup():
    # One-time GL setup
    glClearColor(1, 1, 1, 1)#чем очищать буферы
    glColor3f(1, 0, 0)#ПРОСТО установка цвета. Чему - вообще непонятно. Но это - красный.
    glEnable(GL_DEPTH_TEST)#короче, если это выключить, объекты расположенные "ниже"
    #не будут перекрываться верхнимиОМСКОМСКОМСК
    glEnable(GL_CULL_FACE)#не видимые поверхности вообще не рисуются. Произво-
    #дительность и т.д. Есть подводные камни.

    # Uncomment this line for a wireframe view
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always 
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    # Define a simple function to create ctypes arrays of floats:
    def vec(*args):
        return (GLfloat * len(args))(*args)
    '''
    Ниже включается освещение. Каждая функция создает источник света, указывает
    как и куда он будет светить. Собственно вектором задается именно направление.
    Для его создания используется маленькая функция выше. Мы будем использовать 
    numpy скорее всего
    '''
    glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))
    '''
    Это вообще. Ну тип свойства материала, как он реагирует на освещение.
    '''
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

class Cube(object):
   
    def __init__(self, size, batch):
        # Create the vertex and normal arrays.
 
        vertices = []
        normals = []
        for x in range(size): #прбегаемся по вершинам куба - если размер 1.
            #если размер n - хуй знает чего, ну смотри ниже
            for y in range(size):
                for z in range(size):
                    vertices.extend([x,y,z])
  
        print(vertices)
        print(len(vertices)//3)
        '''
        Почему то я решил, что если забить определенный выше массив
        координат в функцию тора, получиться куб. ХУЙ ТАМ. Я долго не мог 
        впереть, и вот что сделал. Следующая строка рисует точки в 
        беря последовательные числа из массива как координаты - получается
        шняжка.
        '''
       # self.vertex_list = batch.add(len(vertices)//3, GL_POINTS, None, 
       #                              ('v3f/static', (vertices)))
        '''
        Такая хрень рисует непонятные полоски. Ну, как бы, точка может быть
        задана тремя координатами. Если рисовать по точке на каждые тройки из 
        vertices получиться трехмерная сетка из точек (внезапно). Кубик по идее
        должен использовать _восемь_ троек. Синтаксис этой хитрой команды 
        такой: len(vertices)//3 это длина массива, то есть size^3. GL_QUADS 
        это что рисовать (но КАК рисовать? нигде не сказано!), None это то что
        никакой группы нам не нужно. Далее сам массив координат. Почему он рисует
        эти полоски именно так? В каком порядке читает координаты?
        '''
        #self.vertex_list = batch.add(len(vertices)//3, GL_QUADS, None, 
        #                             ('v3f/static', (vertices)))
        '''
        Пробуем полигон - очевидно в нем координаты считаются еще по другому.
        Вопрос- как заставить его рисовать по другому? Короче- если задать размер 
        1, то координаты восьми вершин куба он считает и заносит в массив.
        Как его нарисовать?
        '''
        self.vertex_list = batch.add(len(vertices)//3, GL_POLYGON, None, 
                                     ('v3f/static', (vertices)))                            
                                    
                                    
    def delete(self):
        self.vertex_list.delete()

setup()
batch = pyglet.graphics.Batch()
torus = Cube(20, batch=batch) 
rx = ry = rz = 0

pyglet.app.run()
