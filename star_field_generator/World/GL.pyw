from OpenGL.GL import *
from OpenGL.GLU import *
def resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.5, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glEnable(GL_TEXTURE_2D)

    glEnable(GL_BLEND)                                          #masking functions
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
##    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable( GL_ALPHA_TEST )
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

##    glPushMatrix()
##    glLoadIdentity()
##    LightAmbient  = ( (0.5, 0.5, 0.5, 1.0) );
##    LightDiffuse  = ( (1.0, 1.0, 1.0, 1.0) );
##    LightPosition = ( (0.0, 5.0, 0.0, 1.0) );
##    glLightfv( GL_LIGHT0, GL_AMBIENT, LightAmbient )
##    glLightfv( GL_LIGHT0, GL_DIFFUSE, LightDiffuse )
##    glLightfv( GL_LIGHT0, GL_POSITION, LightPosition )
##    glEnable( GL_LIGHT0 )
##    glPopMatrix()
