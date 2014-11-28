import pyglet
from pyglet.gl import *
 
win = pyglet.window.Window()
 
@win.event
def on_draw():
 
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT)
 
        # Draw some stuff
        glBegin(GL_TRIANGLES)
        glVertex3f(50, 50,1)
        glTexture3f(1,1,1)
        glVertex3f(75, 100,1)
        glVertex3f(100, 150,-100)
        glEnd()
 
pyglet.app.run()