#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-
'''
Kamiken OpenGl v0.0.1




'''

import pyglet
import numpy as np
import random
from pyglet.gl import *
from pyglet import image #<==for image calls
from pyglet.window import key #<==for key constants
from OpenGL.GLUT import * #<==Needed for GLUT calls

'''
Переменные 
'''
BOARD_W = 5
BOARD_H = 1
MSG = 'KAMI~!!'
TILE_SIZE = 300
FONT = 'Comic Sans MS'
WINDOW_W = BOARD_W * TILE_SIZE + 2 * TILE_SIZE
WINDOW_H = BOARD_H * TILE_SIZE + 2 * TILE_SIZE


'''
Изображения
'''
image   = pyglet.resource.image( 'image5.png'     )
r_stone = pyglet.resource.image( 'r_stone.png'   )
#r_stone = pyglet.resource.image( 'NeHe.bmp'   )
r_board = pyglet.resource.image( 'r_board.png'   )

'''
Поле
'''
#ALL_STONES = np.zeros([BOARD_W, BOARD_H])

#for i in range(BOARD_W):
#    for j in range(BOARD_H):
#        ALL_STONES[i,j] = random.randint(0,5)

colors = {   'white'  : (255, 255, 255, 0.3),
             'red'    : (255, 0, 0, 0.3),
             'blue'   : (0, 0, 255, 0.3),
             'board'  : (0.59, 0.54, 0.51, 0.3),
             'r_stone': (243, 104, 18, 255),
             'b_stone': (14, 193, 225, 255)          }



class Board(pyglet.window.Window):

    def __init__(self):
        config = Config(sample_buffers=1, samples=4,
                depth_size=5, double_buffer=True,)
        try:
                super(Board, self).__init__(resizable=True, config=config)
        except:
                super(Board, self).__init__(resizable=True)
        self.setup()
    
    def setup(self):
        self.width = 640
        self.height = 480
        self.xrot = self.yrot = self.zrot = 0.0
        self.texture = None
        self.InitGL(self.width, self.height)
        pyglet.clock.schedule_interval(self.update, 1/60.0) # update at 60Hz
        self.LoadTextures()
        self.STONES = []
        for i in range(BOARD_W):
            for j in range(BOARD_H):
                self.STONES.append([i,j])

    def update(self,dt):
        image.blit(x=0, y=0)
        self.DrawGLScene()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def on_draw(self):
        image.blit(x=0, y=0)
        self.DrawGLScene()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def on_resize(self,w,h):
        self.ReSizeGLScene(w,h)

    def LoadTextures(self):
        self.texture = r_stone.get_texture()
        ix = r_stone.width
        iy = r_stone.height
        rawimage = r_stone.get_image_data()
        format = 'RGBA'
        pitch = rawimage.width * len(format)
        #replaced 'image' with 'myimage', as 'image' is in pyglet namespace
        myimage = rawimage.get_data(format, pitch)

        #comments in the original code
        # Create Texture
        # There does not seem to be support for this call or the version of PyOGL I have is broken.
        #glGenTextures(1, texture)
        #glBindTexture(GL_TEXTURE_2D, texture)   # 2d texture (x and y size)

        #using pyglet image functions
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)

        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, myimage)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    # A general OpenGL initialization function.  Sets all of the initial parameters.
    def InitGL(self,Width, Height):             # We call this right after our OpenGL window is created.
        #glClearColor(0.1, 0.1, 0.1, 0.0)       # This Will Clear The Background Color To Black
        glClearDepth(1.0)                         # Enables Clearing Of The Depth Buffer
        glDepthFunc(GL_LESS)                      # The Type Of Depth Test To Do
        glEnable(GL_DEPTH_TEST)                 # Enables Depth Testing
        glShadeModel(GL_SMOOTH)             # Enables Smooth Color Shading
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()                          # Reset The Projection Matrix
                                                    # Calculate The Aspect Ratio Of The Window
        #(pyglet initializes the screen so we ignore this call)
        #gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    # The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
    def ReSizeGLScene(self,Width, Height):
        if Height == 0:                           # Prevent A Divide By Zero If The Window Is Too Small
              Height = 1
        glViewport(0, 0, Width, Height)     # Reset The Current Viewport And Perspective Transformation
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    # The main drawing function.
    def DrawGLScene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear The Screen And The Depth Buffer
        glLoadIdentity()                    # Reset The View
        glTranslatef(-5.0,-5.0,-20.0)          # Move Into The Screen

        glRotatef(self.xrot,1.0,0.0,0.0)            # Rotate The Cube On It's X Axis
        glRotatef(self.yrot,0.0,1.0,0.0)            # Rotate The Cube On It's Y Axis
        glRotatef(self.zrot,0.0,0.0,1.0)            # Rotate The Cube On It's Z Axis
        Move = 0.0
        #using pyglet image reference
        glBindTexture(self.texture.target, self.texture.id)
        for i in range(BOARD_W):
            for j in range(BOARD_H):
                glLoadIdentity()
                glTranslatef(Move,-5.0,-20.0)
           # print(i,j)
                glBegin(GL_QUADS)               # Start Drawing The Cube
       # Front Face (note that the texture's corners have to match the quad's corners)
                glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, -1.0,  0.2)    # Bottom Left Of The Texture and Quad
                glTexCoord2f(1.0, 0.0); glVertex3f( 1.0, -1.0,  0.2)    # Bottom Right Of The Texture and Quad
                glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0,  0.2)    # Top Right Of The Texture and Quad
                glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0,  0.2)    # Top Left Of The Texture and Quad

        # Back Face
                glTexCoord2f(1.0, 0.0); glVertex3f(-1.0, -1.0, 0.2)    # Bottom Right Of The Texture and Quad
                glTexCoord2f(1.0, 1.0); glVertex3f(-1.0,  1.0, 0.2)    # Top Right Of The Texture and Quad
                glTexCoord2f(0.0, 1.0); glVertex3f( 1.0,  1.0, 0.2)    # Top Left Of The Texture and Quad
                glTexCoord2f(0.0, 0.0); glVertex3f( 1.0, -1.0, 0.2)    # Bottom Left Of The Texture and Quad

        # Top Face
                glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0, 0.2)    # Top Left Of The Texture and Quad
                glTexCoord2f(0.0, 0.0); glVertex3f(-1.0,  1.0, 0.2)    # Bottom Left Of The Texture and Quad
                glTexCoord2f(1.0, 0.0); glVertex3f( 1.0,  1.0,  0.2)    # Bottom Right Of The Texture and Quad
                glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0, -0.2)    # Top Right Of The Texture and Quad

        # Bottom Face
                glTexCoord2f(1.0, 1.0); glVertex3f(-1.0, -1.0, -0.2)    # Top Right Of The Texture and Quad
                glTexCoord2f(0.0, 1.0); glVertex3f( 1.0, -1.0, -0.2)    # Top Left Of The Texture and Quad
                glTexCoord2f(0.0, 0.0); glVertex3f( 1.0, -1.0,  0.2)    # Bottom Left Of The Texture and Quad
                glTexCoord2f(1.0, 0.0); glVertex3f(-1.0, -1.0,  0.2)    # Bottom Right Of The Texture and Quad

        # Right face
                glTexCoord2f(1.0, 0.0); glVertex3f( 1.0, -1.0, -0.2)    # Bottom Right Of The Texture and Quad
                glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0, -0.2)    # Top Right Of The Texture and Quad
                glTexCoord2f(0.0, 1.0); glVertex3f( 1.0,  1.0,  0.2)    # Top Left Of The Texture and Quad
                glTexCoord2f(0.0, 0.0); glVertex3f( 1.0, -1.0,  0.2)    # Bottom Left Of The Texture and Quad   

        # Left Face
                glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, -1.0, -0.2)    # Bottom Left Of The Texture and Quad
                glTexCoord2f(1.0, 0.0); glVertex3f(-1.0, -1.0,  0.2)    # Bottom Right Of The Texture and Quad
                glTexCoord2f(1.0, 1.0); glVertex3f(-1.0,  1.0,  0.2)    # Top Right Of The Texture and Quad
                glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0, -0.2)    # Top Left Of The Texture and Quad

                glEnd();                # Done Drawing The Cube
                Move += 2.3 + i
            self.xrot = self.xrot + 0.2                # X rotation
            self.yrot = self.yrot + 0.2                 # Y rotation
            self.zrot = self.zrot + 0.2                 # Z rotation




    def main():
        global window
        # For now we just pass glutInit one empty argument. I wasn't sure what should or could be passed in (tuple, list, ...)
        # Once I find out the right stuff based on reading the PyOpenGL source, I'll address this.
        glutInit(())
        # Select type of Display mode:
        #  Double buffer
        #  RGBA color
        # Alpha components supported
        # Depth buffer
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
        # get a 640 x 480 window
        glutInitWindowSize(640, 480)
        # the window starts at the upper left corner of the screen
        glutInitWindowPosition(0, 0)
        # Okay, like the C version we retain the window id to use when closing, but for those of you new
        # to Python (like myself), remember this assignment would make the variable local and not global
        # if it weren't for the global declaration at the start of main.
        window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")
        # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
        # set the function pointer and invoke a function to actually register the callback, otherwise it
        # would be very much like the C version of the code.
        glutDisplayFunc (DrawGLScene)   #we do a call from the self.on_draw() method
        # Uncomment this line to get full screen.
        #glutFullScreen()
        # When we are doing nothing, redraw the scene.
        glutIdleFunc(DrawGLScene)
        # Register the function called when our window is resized.
        glutReshapeFunc (ReSizeGLScene)   #we do a call from the
        # Register the function called when the keyboard is pressed.
        glutKeyboardFunc (keyPressed)
        # Initialize our window.
        InitGL(640, 480)
        # Start Event Processing Engine
        glutMainLoop()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            window.close()
        if symbol == key.RETURN:
            window.set_fullscreen(True)


if __name__ == "__main__":
    window = Board()

    pyglet.app.run()



