#!/usr/bin/env python3
#  - * -  coding: UTF - 8  - * - 

import pyglet
from pyglet.gl import *
from pyglet.window import *
import numpy as np
from math import copysign

#from BASIC_SHAPES import Cube

import ctypes

def vec(*args):
	return (GLfloat * len(args))(*args)

class Player(object):
	"""
	Класс игрока. 4 группы координат по каждой из осей.
	pos — позиция в мире
	rot — направление, в которое смотрит
	strafe — для движения вбок.
	xp, yp, zp — промежуточные координаты, без них стрейф не сделать. Впрочем,
	и с ними что-то сбивается.
	height — высоа "головы" игрока над землёй.
	!!В collision detection'ах используются координаты ног!!
	"""
	def __init__(self):
		self.xpos = 1
		self.ypos = 1
		self.zpos = 1
		
		self.xrot = 0
		self.yrot = 0
		self.zrot = 0
		
		self.xstrafe = 0
		self.ystrafe = 0
		self.zstrafe = 0
	
		self.xp = 0
		self.yp = 0
		self.zp = 0
		
		self.height = 2
		self.stepheight = 1
		self.speed = 0.1
		
class Cubecol(object):
	def __init__(self, side, batch, offset=(0,0,0), center = False, type = 'outside', group = None):
		vertices = np.array([	1,0,0, 0,0,0, 1,1,0, 0,1,0, 1,1,1, 0,1,1, 1,0,1, 0,0,1,
								1,1,0, 1,1,1, 1,0,0, 1,0,1, 0,0,0, 0,0,1, 0,1,0, 0,1,1
							])
		if center:
			vertices = vertices-0.5
		
		vertices = vertices.astype(float)
		
		for i in range(0,len(vertices),3):
			vertices[i] = vertices[i] + offset[0]
			vertices[i+1] = vertices[i+1] + float(offset[1])
			vertices[i+2] = vertices[i+2] + float(offset[2])
	
		vertices = vertices*side
	
	
		if type == "outside":
			indices = 	[	0,1,2, 2,1,3, 2,3,4, 4,3,5, 4,5,6, 6,5,7, 
							8,9,10, 10,9,11, 10,11,12, 12,11,13, 12,13,14, 14,13,15	
						]
		elif type == "inside":
			indices = 	[	0,2,1, 2,3,1, 2,4,3, 4,5,3, 4,6,5, 6,7,5, 
							8,10,9, 10,11,9, 10,12,11, 12,13,11, 12,14,13, 14,15,13	
						]

		self.vertex_list = batch.add_indexed(16, GL_TRIANGLES, group, indices, 
											('v3f',vertices))#,('n3f',norm),('t2f',textcoord))
		
		self.collision_box(vertices,offset,side)
	
	def collision_box(self,vertices,offset,side):
		self.zback = vertices[2]
		self.zfront = self.zback + side
		self.ybot = vertices[1]
		self.ytop = self.ybot + side
		self.xleft = vertices[3]
		self.xright = self.xleft + side

class World(Window):
	def __init__(self,player):
		config = Config(sample_buffers=1, samples=4, 
						depth_size=16, double_buffer=True,)
		super(World, self).__init__(config=config, resizable=True, fullscreen=False, vsync=True)
		self.batch = pyglet.graphics.Batch()
		self.batch_box = pyglet.graphics.Batch()
		self.fps = pyglet.clock.ClockDisplay()
		pyglet.clock.schedule_interval(self.update, 1.0 / 60)
		self.player = player
		self.make_cubes()
	
	def make_cubes(self):
		self.cubes = []
		cube = Cubecol(4, self.batch, offset=(-0.5, -2, -0.25))
		self.cubes.append(cube)
		for i in range(1,4):
			cube = Cubecol(2,self.batch, offset=(-0.5,-i*0.5-4,-i-0.5))
			self.cubes.append(cube)
		self.box = Cubecol(20,self.batch,center = True, type = "inside")
		cube = Cubecol(2,self.batch,offset=(-4,-5,-3))
		self.cubes.append(cube)
		cube = Cubecol(2,self.batch,offset=(3,-5,-2))
		self.cubes.append(cube)
		cube = Cubecol(2,self.batch,offset=(4,-5,3))
		self.cubes.append(cube)
		cube = Cubecol(2,self.batch,offset=(-4,-5.6,1.5))
		self.cubes.append(cube)

	
	def update(self, dt):
		for key in keystate:
			if keystate[key]:
				self.dispatch_event('on_key_press',key,False)
		pass
		
	def setup3d(self):
		glViewport(0, 0, self.width, self.height) 
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(60., self.width / float(self.height), .1, 100.)
		glMatrixMode(GL_MODELVIEW)
		glClearColor(0.2, 0.2, 0.2, 1)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glEnable(GL_CULL_FACE)
		glEnable(GL_LIGHTING)
# 		glEnable(GL_LIGHT0)
		glEnable(GL_LIGHT1)
# 		glLightfv(GL_LIGHT0, GL_POSITION, vec(0, 5, 0, 1))
# 		glLightfv(GL_LIGHT0, GL_AMBIENT, vec(1,1,1,0))
# 		glLightfv(GL_LIGHT0, GL_LINEAR_ATTENUATION, vec(0))
		glLightfv(GL_LIGHT1, GL_AMBIENT, vec(1,1,1,0))
		glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(1,1,1,0))
		glLightfv(GL_LIGHT1, GL_LINEAR_ATTENUATION, vec(0.5))
	
	def setup2d(self):
		glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, vec(0,0,0,1))
		glColor3ub(255,255,255)
		glDisable(GL_DEPTH_TEST)
		glViewport(0, 0, self.width, self.height) 
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def ground_collision(self):
		for cube in self.cubes:
			if (cube.zback <= -self.player.zpos < cube.zfront and 
					cube.xleft <= self.player.xpos < cube.xright):
				if cube.ytop - 2 <= self.player.ypos:
					self.player.ypos = cube.ytop
					return
		self.player.ypos = self.box.ybot
	
	def object_collision(self,wsad):
		rot = (np.cos((self.player.yrot+wsad)*np.pi/180),np.sin((self.player.yrot+wsad)*np.pi/180))
		## North-East
		if rot[0]>=0 and rot[1]>=0:
			## Map limit
			if (-self.player.zpos < self.box.zback + 0.4 or self.player.xpos > self.box.xright - 0.4):
				self.player.speed = 0
				return
			for cube in self.cubes:
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.xleft <= self.player.xpos <= cube.xright and 
						cube.zfront < -self.player.zpos < cube.zfront + 0.4):
					self.player.speed = 0
					return
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.zback <= -self.player.zpos <= cube.zfront and 
						cube.xleft - 0.4 < self.player.xpos < cube.xleft):
					self.player.speed = 0
					return
		## North-West
		if rot[0]>=0 and rot[1]<0:
			## Map limit
			if (-self.player.zpos < self.box.zback + 0.4 or self.player.xpos < self.box.xleft + 0.4):
				self.player.speed = 0
				return
			for cube in self.cubes:
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.xleft <= self.player.xpos <= cube.xright and 
						cube.zfront < -self.player.zpos < cube.zfront + 0.4):
					self.player.speed = 0
					return
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.zback <= -self.player.zpos <= cube.zfront and 
						cube.xright + 0.4 > self.player.xpos > cube.xright):
					self.player.speed = 0
					return
		## South-West
		if rot[0]<0 and rot[1]<0:
			## Map limit
			if (-self.player.zpos > self.box.zfront - 0.4 or self.player.xpos < self.box.xleft + 0.4):
				self.player.speed = 0
				return
			for cube in self.cubes:
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.xleft <= self.player.xpos <= cube.xright and 
						cube.zback - 0.4 < -self.player.zpos < cube.zback):
					self.player.speed = 0
					return
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.zback <= -self.player.zpos <= cube.zfront and 
						cube.xright + 0.4 > self.player.xpos > cube.xright):
					self.player.speed = 0
					return
		## South-East
		if rot[0]<0 and rot[1]>=0:
			## Map limit
			if (-self.player.zpos > self.box.zfront - 0.4 or self.player.xpos > self.box.xright - 0.4):
				self.player.speed = 0
				return
			for cube in self.cubes:
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.xleft <= self.player.xpos <= cube.xright and 
						cube.zback - 0.4 < -self.player.zpos < cube.zback):
					self.player.speed = 0
					return
				if (cube.ybot - self.player.height <= self.player.ypos < cube.ytop - self.player.stepheight and
						cube.zback <= -self.player.zpos <= cube.zfront and 
						cube.xleft - 0.4 < self.player.xpos < cube.xleft):
					self.player.speed = 0
					return
		self.player.speed = 0.1
		return
					
	def on_draw(self):
		self.setup3d()
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glRotatef(self.player.xrot,1,0,0)
		glRotatef(self.player.yrot,0,1,0)
		self.ground_collision()
		glLightfv(GL_LIGHT1, GL_POSITION, vec(0,1,4,1))
		glTranslatef(-self.player.xpos,-self.player.ypos-self.player.height,self.player.zpos)
# 		glLightfv(GL_LIGHT1, GL_POSITION, vec(0,1,2,1))
		glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, vec(1,0,0,0))
		self.batch.draw()
		glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, vec(0,1,0,0))
		self.batch_box.draw()
		self.setup2d()
		self.fps.draw()

	def on_mouse_motion(self,x,y,dx,dy):
		self.player.yrot += dx/3
		self.player.xrot -= dy/3
		pass

	def on_key_press(self,symbol,modifier):
		if symbol == key.RETURN:
			keystate[symbol] = False
			self.set_fullscreen(self.fullscreen^True)
			self.set_mouse_visible(self.visible^True)
		if symbol == key.T:
			keystate[symbol] = False
			print("PLAYER POSITION")
			print(self.player.xpos, self.player.ypos, self.player.zpos)
			print("CUBES POSITIONS")
			for cube in self.cubes:
				print(cube.xleft, cube.ybot, cube.zback)
				print(cube.xright, cube.ytop, cube.zfront)
		if symbol == key.ESCAPE:
			keystate[symbol] = False
			self.close()
		if symbol == key.R:
			self.player.xrot += 2
		if symbol == key.F:
			self.player.xrot -= 2		
		if symbol == key.E:
			self.player.yrot += 3
		if symbol == key.Q:
			self.player.yrot -= 3
		if symbol == key.D:
			self.object_collision(90)
			self.player.xstrafe += np.sin((90-self.player.yrot)*np.pi/180)*self.player.speed
			self.player.zstrafe -= np.cos((90-self.player.yrot)*np.pi/180)*self.player.speed
			self.player.zpos = self.player.zp + self.player.zstrafe
			self.player.xpos = self.player.xp + self.player.xstrafe
# 			if	self.object_collision():
# 				self.player.zpos += np.cos((90-self.player.yrot)*np.pi/180)*0.1
# 				self.player.xpos -= np.sin((90-self.player.yrot)*np.pi/180)*0.1
		if symbol == key.A:
			self.object_collision(270)
			self.player.xstrafe -= np.sin((90-self.player.yrot)*np.pi/180)*self.player.speed
			self.player.zstrafe += np.cos((90-self.player.yrot)*np.pi/180)*self.player.speed
			self.player.zpos = self.player.zp + self.player.zstrafe
			self.player.xpos = self.player.xp + self.player.xstrafe
# 			if	self.object_collision():
# 				self.player.zpos -= np.cos((90-self.player.yrot)*np.pi/180)*0.1
# 				self.player.xpos += np.sin((90-self.player.yrot)*np.pi/180)*0.1
		if symbol == key.W:
# 			zpos = self.player.zpos
# 			xpos = self.player.xpos
			self.object_collision(0)
			self.player.zp += np.cos(self.player.yrot*np.pi/180)*self.player.speed
			self.player.xp += np.sin(self.player.yrot*np.pi/180)*self.player.speed
			self.player.zpos = self.player.zp + self.player.zstrafe
			self.player.xpos = self.player.xp + self.player.xstrafe
# 			self.object_collision((copysign(1,self.player.xpos - xpos),copysign(1,self.player.zpos - zpos)))				
		if symbol == key.S:
			self.object_collision(180)
			self.player.zp -= np.cos(self.player.yrot*np.pi/180)*self.player.speed
			self.player.xp -= np.sin(self.player.yrot*np.pi/180)*self.player.speed
			self.player.zpos = self.player.zp + self.player.zstrafe
			self.player.xpos = self.player.xp + self.player.xstrafe
# 			if	self.object_collision():
# 				self.player.zpos += np.cos(self.player.yrot*np.pi/180)*0.1
# 				self.player.xpos += np.sin(self.player.yrot*np.pi/180)*0.1

		
player = Player()
world = World(player)
keystate = key.KeyStateHandler()
world.push_handlers(keystate)
pyglet.app.run()		