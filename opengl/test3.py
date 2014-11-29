#!/usr/bin/env python
#  - * -  coding: UTF - 8  - * - 



from math import pi, sin, cos

import pyglet
from pyglet.gl import *
from pyglet.window import *

from random import random

import numpy as np

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
	gluPerspective(60., width / float(height), .1, 100.)#это устанавливает как
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
	

@window.event
def on_key_press(symbol,modifier):
	global rx, ry, rz
	if symbol == key.Q:
		rx = (rx + 20)%360
	if symbol == key.A:
		rx = (rx - 20)%360
	if symbol == key.W:
		ry = (ry + 20)%360
	if symbol == key.S:
		ry = (ry - 20)%360
	if symbol == key.E:
		rz = (rz + 20)%360
	if symbol == key.D:
		rz = (rz - 20)%360



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
	glTranslatef(0, 0, CAMDIST)#эта функция двигает "камеру". Сейчас она двигается 
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
	glClearColor(0.2, 0.2, 0.2, 1)#чем очищать буферы
	glColor3f(1, 1, 1)#ПРОСТО установка цвета. Чему - вообще непонятно. Но это - красный.
	glEnable(GL_DEPTH_TEST)#короче, если это выключить, объекты расположенные "ниже"
	#не будут перекрываться верхнимиОМСКОМСКОМСК
	""" Ну это вот как раз включает ту самую проверку глубины объекта/пикселя,
	чтобы наложение объектов друг на друга не зависело от порядка их отрисовки."""
# 	glEnable(GL_CULL_FACE)#не видимые поверхности вообще не рисуются. Произво-
	#дительность и т.д. Есть подводные камни.
	"""
	Отключил — мой треугольничек стал нормално рисоваться.
	Почему-то он считался "задней" частью, и поэтому не рисовал. Хотя когда я его
	поворачивал, он имел более тёмный цвет, чем кольцо.
	"""

	# Uncomment this line for a wireframe view
	#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

	# Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
	# but this is not the case on Linux or Mac, so remember to always 
	# include it.
	glEnable(GL_LIGHTING) 
	""" Главный фонарик. Без него не будет цвета у предмета """
	glEnable(GL_LIGHT0)	
	glEnable(GL_LIGHT1)
	"""
	Дополнительные источники, для всяких отражений/преломлений нужны.
	Всего 8 (до GL_LIGHT8), вот только хрен знает, какая в них разница.
	Вряд ли это ограничение на количество источников света.
	"""

	# Define a simple function to create ctypes arrays of floats:
	def vec(*args):
		return (GLfloat * len(args))(*args)
	'''
	Ниже включается освещение. Каждая функция создает источник света, указывает
	как и куда он будет светить. Собственно вектором задается именно направление.
	Для его создания используется маленькая функция выше. Мы будем использовать 
	numpy скорее всего
	'''
	# Ну там не просто маленькая функция, а именно передлка массива в вид С,
	# безо всяких оверхедов, в один буффер подряд все данные запихивает, чтобы не быть МЕДЛЕННЫМ :3
	# Нампи почти то же самое и делает, вроде как.
	glLightfv(GL_LIGHT0, GL_POSITION, vec(10, 10, 10, 0))
	glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
	glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
	glLightfv(GL_LIGHT1, GL_POSITION, vec(-10, -10, -10, 0))
	glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(0, 1, .5, 1))
	glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 0, 0, 1))
	'''
	Это вообще. Ну тип свойства материала, как он реагирует на освещение.
	'''
	glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0, 0, 0.3, 1)) 
	""" Цвет получаеющейся фигуры. """
	glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 0.5, 1, 1))
	"""
	Тоже как-то связано с отржением света во время поворотов. Фигура как-то становится
	всё ярче и ярче, потом максимальная яркость (следующей функцией как-то управляется),
	а затем на секунду меняется цвет на тот, что указан в gl_specular.
	"""
	glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)	
	""" 
	Блёстки всякие, когда предмет повёрнут сильно. Если ноль — просто меняет цвет мгновенно
	на более яркий. Если цифра — хуй знает. Я вижу разницу между 1 и всеми 
	другими — с 1 цвет в самый последний момент поворота намного ярче, чем с другим числом.
	Других отличий чота нет. Но максимальное значение — 1024. Может с большим количеством
	треугольников что-то будет изменяться.
	"""

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

class Square(object):
	"""
	Квадрат из множества треугольников. Параметры:
	side - длина стороны (в тех же единицах, в которых всё измеряется. Километры, навреное.)
	triangles - количество пар треугольников на одну "полосу". Грубо говоря, разрешение
	квадрата, из скольких кусочков собирается.
	axis — две оси, плоскости которых принадлежит квадрат ('xy', 'xz', 'yz')
	level - в завимости от плоскости, это может быть зад/перед, лево/право, низ/верх,
	принимает значения -1 и 1.
	"""
	list = None
	def __init__(self, side, triangles, axis, level, batch, group=None):
		side = float(side)
		step = side/triangles # side уже float
		indices = []
		vertices = []
		"""		
		Вот так выглядит построение одного квадрата в одной плоскости (xy в данном
		случае). Центр в начале координат. Список состоит из координат точек
		по столбцам сверху вниз справа налево. Координате Z придаётся значение
		± половина стороны квадрата, чтобы сдвинуть его на нужно расстояние
		для создания куба
		for i in range(0,triangles):
			for j in range(0,triangles):
				vertices.extend([(side/2)-i*step, (side/2)-j*step,level*(side/2)])
		"""


		"""
		Чуть боллее сложный/запутанный способ для возможности создания квадрата
		в разных плоскостях без банального копирования кода три раза. Интересно жи.
		Принцип работы: создаётся лямба функция, в которой в зависимости от
		выбранной плоскости выбирается начало для трёх элементов.
		"""
		abs_axis = ['xy','xz','yz'].index(axis)
		verts = lambda: [(side/2)-i*step, (side/2)-j*step, level*(side/2),
							(side/2)-i*step, (side/2)-j*step][abs_axis:abs_axis+3]
	
		for i in range(0,triangles):
			for j in range(0,triangles):
				vertices.extend(verts())

		"""
		Ну и банальное с if'ами
		if axis == "xy":
			for i in range(0,triangles):
				for j in range(0,triangles):
					vertices.extend([(side/2)-i*step, (side/2)-j*step,level*(side/2)])
		elif axis == "xz":
			for i in range(0,triangles):
				for j in range(0,triangles):
					vertices.extend([(side/2)-i*step, level*(side/2), (side/2)-j*step])
		elif axis == "yz":
			for i in range(0,triangles):
				for j in range(0,triangles):
					vertices.extend([level*(side/2), (side/2)-i*step, (side/2)-j*step])
		"""			
					

		
		
		""" Индексы получаются одинаково независимо от плоскости/положения. Грубо говоря,
		первая строка получает тругольник А, вторая — B. Индексы выбираются 
		следующим образом, где А123 — первая строка, В123 — вторая:
		x A2 A1 ++ x B2 x  || x x  x  ++ x x  x  || A2 A1 x ++ B2 x  x || x  x  x ++ x  x  x
		x x  A3 ++ x B3 B1 || x A2 A1 ++ x B2 x  || x  A3 x ++ B3 B1 x || A2 A1 x ++ B2 x  x
		x x  x  ++ x x  x  || x X  A3 ++ x B3 B1 || x  x  x ++ x  x  x || x  A3 x ++ B3 B1 x
		Как можно заметить, особо не важно, построчно или постолбцово создавались
		вершины, поэтому смена местами двух значимых аргументов в vertices.extend([])
		не оказывает никакого влияения на построенную фигуру.
		"""

		for i in range(triangles-1):
			for j in range(triangles-1):
				indices.extend([triangles * i + j, triangles * (i+1) + j, triangles * i + j + 1])
				indices.extend([triangles * i + j + 1, triangles * (i+1) + j, triangles * (i+1) + j + 1])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
   											 ('v3f/static', vertices))

	def delete(self):
		self.vertex_list.delete()
		
class Circle(object):
	"""
	Дело круг на много треугольников с одной общей вершиной (в центре).
	Создаётся всего slice+2 вершины, каждый новый труегольник строится по двум старым
	и одной новой вершинам (имеет общую сторону с предыдущим).
	depth — глубина по оси z. Используется для приближения/отдаления круга при построении 
	цилиндра или конуса.
	"""
	list = None
	def __init__(self, radius, slices, depth, batch, group=None):
		r = radius
		vertices = []
		indices = []
		step = (2 * pi) / (slices) # шаг построения треугольников
		
		vertices.extend([0, 0, depth])	# центр круга
		
		"""
		Грубо говоря, ставим точки на окружности с определённым шагом. 
		"""
		for i in range(0,slices+1):
			vertices.extend([r*sin(step*i),r*cos(step*i),depth])
		
		"""
		Центр и две соседние точки на окружности соединяются в один треугольник.
		"""		
		for i in range(0,slices):
			indices.extend([0, i+1, i+2])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
   											 ('v3f/static', vertices))

	def delete(self):
		self.vertex_list.delete()

class Belt(object):
	"""
	Создаёт кольцо, имеющее некоторую плошадь.
	"""
	list = None
	def __init__(self, radius, slices, width, batch, group=None):
		r = radius
		vertices = []
		indices = []
		step = (2 * pi) / (slices)
		width = width 	# ширина кольца
		
		""" 
		Первые две точки. Необходимо создать до лупа, так как в лупе другой порядок
		добавления вертексов в список.
		"""
		vertices.extend([r*sin(0),r*cos(0),width/2.])
		vertices.extend([r*sin(0),r*cos(0),-width/2.])
		"""
 		Почти то же самое, что и в случае с кругом, только тут ставятся
 		точки на две как бы чуть отстоящие друг от друга окружности.
 		"""
		for i in range(1,slices+1):
			vertices.extend([r*sin(step*i),r*cos(step*i),-width/2.])
			vertices.extend([r*sin(step*i), r*cos(step*i),width/2.])


		"""
		Опять же, первые две точки являются каким-то исключением, из-за нуля эти два
		набора вершин не подходят под алгоритм в нижестоящем цикле.
		"""
		indices.extend([0,1,2, 0,2,3])

		"""
		Создаёт два треугольника на "поверхности" кольца, образующих маленький
		прямоугольник. Разумно было бы перенять алгоритм из квадрата, он логичней, вроде как.
		"""
		for i in range(0,slices):
			indices.extend([i*2+1,i*2,i*2+2])
			indices.extend([i*2+1,i*2+2,i*2+3])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
   											 ('v3f/static', vertices))

	def delete(self):
		self.vertex_list.delete()

class Belt2(object):
	"""
	Колько в другой плоскости.
	"""
	list = None
	def __init__(self, radius, slices, width, batch, group=None):
		r = radius
		vertices = []
		indices = []
		step = (2 * pi) / (slices)
		width = width 	# ширина кольца
		
		""" 
		Первые две точки. Необходимо создать до лупа, так как в лупе другой порядок
		добавления вертексов в список.
		"""
		vertices.extend([r*sin(0),width/2., r*cos(0)])
		vertices.extend([r*sin(0),-width/2., r*cos(0)])
		"""
 		Почти то же самое, что и в случае с кругом, только тут ставятся
 		точки на две как бы чуть отстоящие друг от друга окружности.
 		"""
		for i in range(1,slices+1):
			vertices.extend([r*sin(step*i),-width/2., r*cos(step*i)])
			vertices.extend([r*sin(step*i),width/2., r*cos(step*i)])


		"""
		Опять же, первые две точки являются каким-то исключением, из-за нуля эти два
		набора вершин не подходят под алгоритм в нижестоящем цикле.
		"""
		indices.extend([0,1,2, 0,2,3])

		"""
		Создаёт два треугольника на "поверхности" кольца, образующих маленький
		прямоугольник. Разумно было бы перенять алгоритм из квадрата, он логичней, вроде как.
		"""
		for i in range(0,slices):
			indices.extend([i*2+1,i*2,i*2+2])
			indices.extend([i*2+1,i*2+2,i*2+3])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
   											 ('v3f/static', vertices))

	def delete(self):
		self.vertex_list.delete()

class Belt3(object):
	"""
	Колько в другой плоскости.
	"""
	list = None
	def __init__(self, radius, slices, width, batch, group=None):
		r = radius
		vertices = []
		indices = []
		step = (2 * pi) / (slices)
		width = width 	# ширина кольца
		
		""" 
		Первые две точки. Необходимо создать до лупа, так как в лупе другой порядок
		добавления вертексов в список.
		"""
		vertices.extend([width/2.,r*sin(0),r*cos(0)])
		vertices.extend([-width/2.,r*sin(0),r*cos(0)])
		"""
 		Почти то же самое, что и в случае с кругом, только тут ставятся
 		точки на две как бы чуть отстоящие друг от друга окружности.
 		"""
		for i in range(1,slices+1):
			vertices.extend([-width/2.,r*sin(step*i),r*cos(step*i)])
			vertices.extend([width/2.,r*sin(step*i),r*cos(step*i)])


		"""
		Опять же, первые две точки являются каким-то исключением, из-за нуля эти два
		набора вершин не подходят под алгоритм в нижестоящем цикле.
		"""
		indices.extend([0,1,2, 0,2,3])

		"""
		Создаёт два треугольника на "поверхности" кольца, образующих маленький
		прямоугольник. Разумно было бы перенять алгоритм из квадрата, он логичней, вроде как.
		"""
		for i in range(0,slices):
			indices.extend([i*2+1,i*2,i*2+2])
			indices.extend([i*2+1,i*2+2,i*2+3])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
   											 ('v3f/static', vertices))

	def delete(self):
		self.vertex_list.delete()

class Cone(object):
	"""
	Типа верхушка конуса. Единственно отличие от круга — центральная точка
	сдвинута по оси Z от остальных.
	"""
	list = None
	def __init__(self, radius, slices, depth, batch, group=None):
		r = radius
		vertices = []
		indices = []
		step = (2 * pi) / (slices) # Шаг построения треугольников.
		
		vertices.extend([0, 0, 0])	# Кончик конуса.
		
		"""
		Грубо говоря, ставим точки на окружности с определённым шагом. 
		"""
		for i in range(0,slices+1):
			vertices.extend([r*sin(step*i),r*cos(step*i),depth])
		
		"""
		Центр и две соседние точки на окружности соединяются в один треугольник.
		"""		
		for i in range(0,slices):
			indices.extend([0, i+1, i+2])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
   											 ('v3f/static', vertices))

	def delete(self):
		self.vertex_list.delete()

class Ring(object):
	
	def __init__(self, radius, inner_radius, slices, inner_slices, depth, batch, group=None):
		r = radius
		ir = inner_radius
		vertices = []
		indices = []
		step = (2*pi) / slices
		istep = (2*pi) / inner_slices
		
		#vertices.extend([0, 0, 0])
		for i in range(0,slices+1):
			vertices.extend([r*sin(step*i),r*cos(step*i),depth])
		#for j in range(0,islices+1):
			vertices.extend([ir*sin(istep*i),ir*cos(istep*i),depth])
			
		for i in range(0,slices*2):
			indices.extend([i, i+1, i+2])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
																	('v3f/static', vertices))

class Sphere(object):
	"""
	Сфера
	"""
	list = None
	def __init__(self, radius, slices, type, batch, group=None):
		r = radius
		vertices = []
		indices = []
		step = (2 * pi) / (slices)
		
		
# 		vertices.extend([r*sin(0),r*cos(0),sin(step)])		
# 		vertices.extend([r*sin(0),r*cos(0),0])

		"""
		for i in range(0,triangles):
			for j in range(0,triangles):
				vertices.extend([(side/2)-i*step, (side/2)-j*step,level*(side/2)])

		for i in range(triangles-1):
			for j in range(triangles-1):
				indices.extend([triangles * i + j, triangles * (i+1) + j, triangles * i + j + 1])
				indices.extend([triangles * i + j + 1, triangles * (i+1) + j, triangles * (i+1) + j + 1])
		"""
 		
# 		for i in range(0,slices):
# 	 		vertices.extend([r*sin(step*i),r*cos(step*i),0])
# 			vertices.extend([r*sin(step*i), r*cos(step*i), sin(step)])
# 
# 		indices.extend([0,1,2, 0,2,3])
# 
# 		for i in range(0,slices):
# 			indices.extend([i*2+1,i*2,i*2+2])
# 			indices.extend([i*2+1,i*2+2,i*2+3])

#		vertices.extend([0,r,0])

		for i in range(0, slices):
			for j in range(0,slices):
				if type=="konvertik":
					vertices.extend([r*sin(step*j)*cos(step*i), r*cos(step*j), r*sin(step*i)*cos(step*j)])
				elif type=="krugtochki":
					vertices.extend([r*sin(step*j)*cos(step*i), r*cos(step*j), 0])
				elif type=="vietnam":
					vertices.extend([r*sin(step*j)*cos(step*i), r*cos(step*j), r*sin(step*j)-abs(r*sin(step*j)*cos(step*i))])
				else:
					pass
		if type=="krugkub":
			"""
			Грубо говоря, коэффициент x уменьшается (имитация проекции и т.д.), потом
			увеличивается. Ну ты понимаешь, думаю.
			А коээфициент z начинает в нул, достигает максимума (когда нужно рисовать
			окружность в плоскости yz), и снова до 0 спадает.
			В идеале, какая-то фунция от i должна создавать подобные списки с
			косинусом/синусом, тогда будет сфера, ведь на самом деле шаги изменения
			коэффициента x и y не равны.
			"""
			coeff_x = [1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,-0.4,-0.5,-0.6,0.7,-0.8,-0.9,-1]
			coeff_z = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0]
			for i in range(0,len(coeff_x)):
				for j in range(0,slices):
					vertices.extend([r*sin(step*j)*coeff_x[i], r*cos(step*j), coeff_z[i]*r*sin(step*j)]) 	

		if type=="sphere":
			"""
			Собственно, то же самое, что и в прошлом, только коэффициенты создаются
			косинусом и синусом. И ведь, чёрт побери, отличие от konvertik'а,
			с которым я полночи просидел, лишь в смене косинуса на синус в коэффициенте
			координаты z.
			В общем, i=0: рисуется окружность в плоскости xy.
			i = 1: рисуется "чуть повёрнутая" окружность, соответственно появляются
			маленькие значения z, а амплитуда x чуть уменьшается для того, чтобы не 
			становиться цилиндром.
			"""
			for i in range(0,slices):
				for j in range(0,slices):
					vertices.extend([r*sin(step*j)*cos(step*i), r*cos(step*j), sin(step*i)*r*sin(step*j)]) 


# 		for i in range(slices-2):
# 			for j in range(slices):
# 				indices.extend([slices * i + j, slices * (i+1) + j, slices * i + j + 1])
# 				indices.extend([slices * i + j + 1, slices * (i+1) + j, slices * (i+1) + j + 1])
	
	
		for i in range(slices-1):
			indices.extend([i*slices+1, 0, (i+1)*slices+1])
			for j in range(slices-1):
				indices.extend([i*slices+j+1, (i+1)*slices+j, i*slices+j+2])
				indices.extend([i*slices+j+1, (i+1)*slices+j, (i+1)*slices+j+2])
	
# 		vertices = [0,1,0, 	0.05,0.95,0, 	0.1,0.9,0, 		0.15,0.85,0, 	0.2,0.8,0, 		0.25,0.75,0,
# 							0.04,0.95,0.01, 0.08,0.9,0.02, 	0.12,0.85,0.03, 0.16,0.8,0.04, 	0.21,0.75,0.05,
# 							0.03,0.95,0.03, 0.06,0.9,0.06, 	0.09,0.85,0.09, 0.12,0.8,0.12, 	0.15,0.75,0.15,
# 							0.01,0.95,0.04, 0.02,0.9,0.08, 	0.03,0.85,0.12, 0.04,0.8,0.16, 	0.05,0.75,0.15]
# 		
# 		indices = [	1,0,6, 1,6,2, 2,6,7, 2,7,3, 3,7,8, 3,8,4, 4,8,9, 4,9,5, 5,9,10,
# 					6,0,11, 6,11,7, 7,11,12, 7,12,8, 8,12,13, 8,13,9, 9,13,14, 9,14,10, 10,14,15,
# 					11,0,16, 11,16,12, 12,16,17, 12,17,13, 13,17,18, 13,18,14, 14,18,19, 14,19,15, 15,19,20]
					
		
#		vr = np.array(vertices)
		
#		vr = np.round(vr,4)
		
#		print(vr)
	
# 		for i in range(0,slices-1):
# 			for j in range(0,(slices-1)):
# 				indices.extend([i*slices, (i+1)*slices, i*slices+1])
# 				indices.extend([i*slices+1, (i+1)*slices, (i+1)*slices+1])
#		indices = [0,1,2, 0,2,3, 3,2,4, 3,4,5, 5,4,6, 5,6,7]

		print (len(indices))
		print (len(vertices))

		
#		 indices = []
#		 for i in range(slices - 1):
#			 for j in range(inner_slices - 1):
#				 p = i * inner_slices + j
#				 indices.extend([p, p + inner_slices, p + inner_slices + 1])
#				 indices.extend([p, p + inner_slices + 1, p + 1])

		self.vertex_list = batch.add_indexed(len(vertices)//3, GL_TRIANGLES, group, indices,
  											 ('v3f/static', vertices))

# 		self.vertex_list = batch.add(len(vertices)//3, GL_POINTS, group,
#    											 ('v3f/static', vertices),
#    											 ('c3B',(0,255,0)*(len(vertices)//3)))


	def delete(self):
		self.vertex_list.delete()


def update(dt):
	'''
	Тут все понятно — вычисляем приращения координат, но возвращает функция в 
	глобальное пространство и не сами координаты, а остаток их деления на 360.
	'''
	global rx, ry, rz
# 	rx += dt * 30
# 	ry += dt * 80
# 	rz += dt * 30
# 	rx %= 360
# 	ry %= 360
# 	rz %= 360
	pass
	
	
def cube(side,triangles,batch):
	""" Кубик такой себе получается, углы не очень. """
	Square(side,triangles,'xy',-1,batch=batch)
	Square(side,triangles,'xy',1,batch=batch)
	Square(side,triangles,'xz',-1,batch=batch)
	Square(side,triangles,'xz',1,batch=batch)
	Square(side,triangles,'yz',-1,batch=batch)
	Square(side,triangles,'yz',1,batch=batch)

def cylinder(radius,depth,slices,batch):
	""" И цилиндр, вроде, норм. """
	Belt(radius,slices,float(depth),batch)
	Circle(radius,slices,depth/2.,batch)
	Circle(radius,slices,-depth/2.,batch)

def cone(radius,slices, height, batch):
	""" Конус и конус. """
	Circle(radius, slices, height, batch)
	Cone(radius, slices, height, batch)
	
def wizzard(radius, slices, height, batch):
	Cone(radius, slices, height, batch)
	Ring(radius*1.3, radius, slices, slices, height, batch)

pyglet.clock.schedule(update)

CAMDIST = -15

setup()
batch = pyglet.graphics.Batch()

""" Чужое """
#torus = Torus(1, 0.3, 30, 30, batch=batch) #можешь поиграться с количсетвом кусочков чтобы увидеть треугольнички 

""" Углы-уголки """
#square = Square(5,3,axis='yz',level=1,batch=batch)
#cube(7,50,batch)

""" Круглые предметы """
#circle = Circle(5, 4, 0, batch=batch)
#belt = Belt(5,50, 2, batch=batch)
#ring = Ring(5, 3, 50, 50, 0, batch=batch)
#cylinder(5,10,50,batch)
#cone(5,50,7,batch)
#wizzard(5, 30, 10, batch)

""" Флагман """
#sphere = Sphere(5,200, 'konvertik', batch=batch)
#sphere = Sphere(5,200, 'krugtochki', batch=batch)
#sphere = Sphere(5,200, 'vietnam', batch=batch)
#sphere = Sphere(5,200, 'krugkub', batch=batch) # http://puu.sh/da0lO/1d4f524a7c.png
sphere = Sphere(5,200, 'sphere', batch=batch)


rx = ry = rz = 0
# ry = 200
# rz = 50

pyglet.app.run()
