#!/usr/bin/env python
#  - * -  coding: UTF - 8  - * - 



from math import pi, sin, cos

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
    """
    Как было там в комментах написано, эта функция как "сбрасывает" матрицу,
    загружая единичную (которая identity matrix по-английски).
    """
    gluPerspective(90., width / float(height), .1, 1000.)#это устанавливает как
    #бы угол зрения что-ли
    """
    Первое да, угол, вот только почему-то его изменение ведёт к изменению размера
    рисуемого анального колечка. Чому так, лол? 
    А второе — соотноешние сторон для поля зрения по оси Х. Видимо, для правильной
    отрисовка круглых объектов на неквадратных плоскостях, ведь все координаты ∈ [0,1]
    Последние две цифры — глубины прорисовки, то есть максимальное расстояние,
    на котором ещё будут рисоваться объекты. Например, в NeHe tutorial 10
    можешь в функции ReSizeGLScene в этой же gluPerspective (у меня 222 строка)
    поиграться с цифрами и увидишь, как поставив 10, 100 — не будут рисоваться близкие,
    а 0.1, 10 — когда далеко из "комнаты" выйдешь - быстро пропадёт всё.
    """
    glMatrixMode(GL_MODELVIEW)#теперь опять работаем с матрицей модельки
    """ Надо бы почитать, что glMatrixMode делает вообще """
    return pyglet.event.EVENT_HANDLED
    '''
    Как будто в опенгле одна матрица для всего? 
    '''
    """ Мне думается, что glMatrixMode как бы выбирает матрицу, на которой потом функции
    вроде glLoadIndentity() и издеваются, но фиг знает."""
    

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
    """
    В одном из видео той серии, что я тееб скинул, как раз это обсуждалось.
    Грубо говоря, каждому пикселю присваивается "дальность" от viewport'а — "камеры зрения",
    и если в одной точке (проецируется же всё на плоскость) уже есть объект на 
    расстоянии 0.5, то если у того же пикселя рисуемого объекта эта глубина больше (то есть,
    он находится "за" уже нарисованным объектом), то пиксель отбрасывается и на экране
    остаётся тот, что был. Если же он ближе — то рисуется "поверх" имевшегося там объекта.
    """
    glLoadIdentity()
    glTranslatef(0, 0, -4)#эта функция двигает "камеру". Сейчас она двигается 
    #"вверх", в сторону зрителя. Можно двигать относительно модели, можно 
    #относительно "перспективы" (туманная фраза, но суть в том, что движение
    #происходит в зависимости от текущей матрицы)
    """ Не очень понял, что там куда двигается. У меня всё на месте, только бублик крутится-вертится."""
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
    """ Ну это вот как раз включает ту самую проверку глубины объекта/пикселя,
    чтобы наложение объектов друг на друга не зависело от порядка их отрисовки."""
    glEnable(GL_CULL_FACE)#не видимые поверхности вообще не рисуются. Произво-
    #дительность и т.д. Есть подводные камни.
    """ Что за невидимые объекты? И как они могут нарисоваться? """

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

class Torus(object):
    list = None
    def __init__(self, radius, inner_radius, slices, inner_slices, 
                 batch, group=None):
        # Create the vertex and normal arrays.
        '''
        Объект делят на ломтики что ли, внутри и снаружи, и вычисляют
        нормали и координтаы к каждому. Матан. Как ты любишь.
        '''
        """
        Это я пока не читал/не разбирался, но обязательно сделаю.
        """
        vertices = []
        normals = []

        u_step = 2 * pi / (slices - 1)
        v_step = 2 * pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = inner_radius * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create a list of triangle indices.
        '''
        Ну то есть создается нужное количество индексов (связанных с
        номерами внутренних и внешних "кусочков") треугольничков, из которых и
        будет объект составлен. 
        '''
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p, p + inner_slices + 1, p + 1])
        '''
        А здесь блять одной командой все это рисуется. Во первых - сразу видно,
        что используется переданный в класс батч - к нему хитрой пиглетовской
        функцией добавляются все нужные объекты и более того, они проиндексированы 
        в соответствии со списком  indices! это можно использовать в нашем текущем
        проекте.
        Дальше- первый аргумент функции это количество объектов.
        Второй аргумент это тип объекта - в опенгл есть в принципе точки, линии,
        треугольники, квадратики и полигоны. Все это может быть н-мерным.
        Дальше  два аргумента указывают, что объекты должны быть объединены
        в группу с такими то индексами.
        Ну дальше... ('v3f/static', vertices) указывает координаты вершин.
        Стандартный опенгл может рисовать если указывать их построчно, как я пытался,
        здесь ему передается массив вершин. При этом передается еще один аргумент 
        - строка, указывающая как интерпритировать полученные вершины. v говорит
        что это вершины, 3 говорит что пространство трехмерное, f что они float,
        /static что они создаются и не меняются. С нормалями аналогично. Магическим
        образом пиглет все понимает и располагает треугольнички нарисованные по двум 
        координатам и относительно нормалей. 
        
        '''
        self.vertex_list = batch.add_indexed(len(vertices)//3, 
                                             GL_TRIANGLES,
                                             group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))
       
    def delete(self):
        self.vertex_list.delete()

setup()
batch = pyglet.graphics.Batch()
torus = Torus(1, 0.3, 30, 30
              , batch=batch) #можешь поиграться с количсетвом кусочков чтобы увидеть треугольнички 
rx = ry = rz = 0

pyglet.app.run()
