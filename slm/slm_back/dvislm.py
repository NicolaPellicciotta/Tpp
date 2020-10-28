from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
from numpy import *
import siteconf
import world

def rad2byte(holo):
	"""Returns a 0..255 hologram from a radians phase holo"""
	lpr=256./2./pi
	return mod(lpr*holo, 256).round().astype(uint8)

class SLMWidget(QtOpenGL.QGLWidget):
  def __init__(self, w, h):
    #super(modulator, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers))
    super(SLMWidget, self).__init__()
    self.w,self.h = w,h
    self._holo=zeros((h,w), dtype=uint8)

    #Qt
    self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    #Textures
    self.makeCurrent()
    self.tex=glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, self.tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.w, self.h,0, GL_LUMINANCE, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)  #Word alignment (ask Lorenzo, CUDA or numpy compatibility?)
    glBindTexture(GL_TEXTURE_2D, 0)

    self.show()
    self.setGeometry(0,0,self.w,self.h)

  def initializeGL(self):
    glClearColor(0.0,0.0,0.0,0.0)
    glEnable(GL_TEXTURE_2D)
 
  def paintGL(self):
    #glViewport(0,0,self.device.w, self.device.h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, self.w, 0, self.h, -20, 20)

    glMatrixMode(GL_MODELVIEW)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glBindTexture(GL_TEXTURE_2D, self.tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.w, self.h, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, self._holo.tostring())

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(0, 0, 0.)
    glTexCoord2f(1, 0); glVertex3f(self.w, 0,  0.)
    glTexCoord2f(1, 1); glVertex3f(self.w, self.h, 0.)
    glTexCoord2f(0, 1); glVertex3f(0, self.h, 0.)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)

  def resizeGL(self, w, h):
    glViewport(0,0,w,h)
  
  def setholo(self, h):
    self._holo=h
    self.repaint()

class DVImodulator:
  def __init__(self):
    if world.slm:
      raise Exception("There's an open SLM in the world")    
    if siteconf.slm == "hamamatsu":
      self.width=800
      self.height=600
      self.lam=1.064
      self.mpp=20.
      self.aberration=siteconf.aberration
      self.lut=None
    if siteconf.slm == "hamamatsu-NIR":
      self.width=800
      self.height=600
      self.lam=0.785
      self.mpp=20.
      self.aberration=siteconf.aberration
      self.lut=None
    elif siteconf.slm == "holoeye":
      self.width=1024
      self.height=768
      self.mpp=19.
      self.lam=0.532
      self.aberration=siteconf.aberration
      self.lut=None

    self.displayedholo=zeros((self.height,self.width),dtype=uint8)
    self.glwidget=SLMWidget(self.width, self.height)
    self.glwidget.setGeometry(1920,0,self.width,self.height)#CHANGE FIRST ARGUMENT WITH MONITOR WIDTH
    world.slm=self

  def show(self, holo):
    assert(shape(holo)==(self.height,self.width))
    #prepare hologram
    if holo.dtype!=uint8:
      self.displayedholo=rad2byte(holo)
    else:
      self.displayedholo=holo
    if self.aberration!=None:
      self.displayedholo+=self.aberration
    #show hologram
    self.glwidget.setholo(self.displayedholo)


