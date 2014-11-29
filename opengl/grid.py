import sys, time, math, os, random
from pyglet.gl import *

window = pyglet.window.Window()

label = pyglet.text.Label('Simulation', 
                          font_name='Times New Roman', 
                          font_size=16,
                          color=(204,204,0,255),      #red font (255,0,0) opacity=255
                          x=window.width, y=window.height,
                          anchor_x='right', anchor_y='top') 

class FilledSquare:
    def __init__(self, width, height, xpos, ypos):
        self.batch = pyglet.graphics.Batch()
        self.xpos = xpos
        self.ypos = ypos
        self.angle = 0
        self.size = 1
        x = width/2.0
        y = height/2.0
        z = 0.2 *height
        self.vlist = pyglet.graphics.vertex_list(8, ('v3f', [-x,-y,-z, x,-y,-z, -x,y,-z, -x,-y,z, x,y,-z, -x,y,z, x,-y,z]), ('t3f', [0,0, 1,0, 0,1, 1,1]), ('c3B',(0,255,0,0,255,0,0,255,0,0,255,0)))
    def draw(self,w,h,x,y):
        self.width=w
        self.height=h
        self.xpos=x
        self.ypos=y
        glPushMatrix()
        glTranslatef(self.xpos, self.ypos, 0)
        self.vlist.draw(GL_QUADS)        
        glPopMatrix()


@window.event
def on_draw():
    window.clear()
    glClearColor(0, 0.3, 0.5, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    label.draw()
    for i in range(5):
        for j in range(5):
            square.draw(30,30,100*i,100*j )
    
    
square = FilledSquare(30, 30, 100, 100)
pyglet.app.run()
