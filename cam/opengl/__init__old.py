from PyQt4 import QtCore, QtOpenGL
from OpenGL.GL import *
from cam.cameras import *
from numpy import float32, uint16, uint8, zeros

libcudagl=ctypes.cdll.LoadLibrary("libcudagl.so")

libcudacam=ctypes.cdll.LoadLibrary("libcudacam.so")
libcudacam.histogram.argtypes=[ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint]
#libcudacam.glmap.restype=ctypes.POINTER(ctypes.c_uint8)
#libcudacam.glmap.restype=ctypes.c_void_p
#libcutils=ctypes.cdll.LoadLibrary("libcutils.dylib")
libcutils=ctypes.cdll.LoadLibrary("libcutils.so")
libcutils.memcpy_subarray.argtypes=[ctypes.c_void_p, ctypes.c_void_p,ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int] 




ErrMsg=ctypes.create_string_buffer(256)

class CudaError(Exception):
	"""Raised when a libcudacam function returns with an error status

	Attributes:
		msg -- cuda error message
	"""
	def __init__(self, msg):
		self.msg=msg.value
	def __str__(self):
		return self.msg

class PBO:
  """A wrapper class for OpenGL Pixel Buffer Objects
  provides methods for mapping data memory address both
  in host space and device space"""
  def __init__(self, size, glcontext, target=GL_PIXEL_UNPACK_BUFFER, access=GL_READ_WRITE, usage=GL_DYNAMIC_DRAW):
    self.size=size
    self.target=target
    self.access=access
    self.usage=usage
    self.res=ctypes.c_int()
    self.glcontext=glcontext

    self.glcontext.makeCurrent()
    self.name=glGenBuffers(1)
    glBindBuffer(self.target, self.name)
    glBufferData(self.target, size, None, usage)
    #glBufferData(self.target, None, usage)
    glBindBuffer(self.target, 0)
    libcudagl.makeCurrent(ErrMsg)
    if libcudagl.regbuf(GLuint(self.name), ctypes.byref(self.res), ErrMsg):
      raise CudaError(ErrMsg)

  def h_map(self):
    self.glcontext.makeCurrent()
    glBindBuffer(self.target, self.name)
    address=glMapBuffer(self.target, self.access)
    glBindBuffer(self.target, 0)
    return address

  def h_unmap(self):
    self.glcontext.makeCurrent()
    glBindBuffer(self.target, self.name)
    glUnmapBuffer(self.target)
    glBindBuffer(self.target, 0)

  def d_map(self):
    address=ctypes.c_void_p()
    self.glcontext.makeCurrent()
    libcudagl.makeCurrent(ErrMsg)
    if libcudagl.glmap(GLuint(self.name), self.res, ctypes.byref(address), ErrMsg):
      raise CudaError(ErrMsg)
    return address

  def d_unmap(self):
    self.glcontext.makeCurrent()
    libcudagl.makeCurrent(ErrMsg)
    if libcudagl.glunmap(GLuint(self.name), self.res, ErrMsg):
      raise CudaError(ErrMsg)

  def clear(self):
    blank=zeros(self.size, dtype=uint8)
    address=self.h_map()
    ctypes.memmove(blank.ctypes.data, address, self.size)
    self.h_unmap()

class CudaGLCam(BaseCam):
  """Extends BaseCam class with:
  -OpenGL pixel buffer objects
  -CUDA rendering of raw frames
  -OpenGL painting function"""

  def __init__(self):
    BaseCam.__init__(self)#super(CudaGLCam, self).__init__()
    #QT OpenGL widget, provides context through makeCurrent() calls (?)
    self.glwidget=QtOpenGL.QGLWidget(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers))

    #self.filters=[]
    #QMutex protects raw_pbo
    #self.raw_pbo_mutex=QtCore.QMutex()

    #CAM params
    #self.cam=CAMERA()
    #self.raw_itemsize=self.cam.dtype(0).itemsize 
    self.raw_itemsize=self.dtype()(0).itemsize 
    
    self.tex_format=GL_RGB
    self.tex_itemsize=3

    #initialize GL
    #self.glwidget.makeCurrent()
    self.glwidget.setAutoFillBackground(False)

    #Texture Buffers
    #siz=self.cam.w*self.cam.h*self.tex_itemsize
    glcontext=self.glwidget.context()
    [w, h]=self.shape()
    siz=w*h*self.tex_itemsize
    self.tex_pbo_idx=0
    self.tex_pbo=[PBO(siz, glcontext), PBO(siz, glcontext)]
    self.tex_pbo_active=self.tex_pbo[self.tex_pbo_idx]
    self.tex_pbo_inactive=self.tex_pbo[(self.tex_pbo_idx+1)%2]

    #Data Buffers
    self.siz=w*h*self.raw_itemsize
    self.raw_pbo = PBO(self.siz, glcontext)
    #siz=w*h*float32().itemsize
    #self.preproc_pbo = PBO(siz, glcontext)

    #Textures
    self.glwidget.makeCurrent()
    self.tex=glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, self.tex)
    #glTexImage2D(GL_TEXTURE_2D, 0, self.tex_format, self.cam.w, self.cam.h,
    glTexImage2D(GL_TEXTURE_2D, 0, self.tex_format, w, h,
                 0, self.tex_format, GL_UNSIGNED_BYTE, None)


    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)  #Word alignment (ask Lorenzo, CUDA or numpy compatibility?)
    glBindTexture(GL_TEXTURE_2D, 0)


    #OpenGL
    glClearColor(0.0,0.0,0.0,0.0)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)


  def paintgl(self,rect,zoom):
    #[xo,yo,w,h]=self.cam.roi()
    self.glwidget.makeCurrent()#TODO: check if needed
    [roix,roiy,roiw,roih]=self.roi()

    glMatrixMode(GL_MODELVIEW)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslated(0.0, 0.0, -10.0)
    glBindBuffer(GL_PIXEL_UNPACK_BUFFER, self.tex_pbo_active.name)
    glBindTexture(GL_TEXTURE_2D, self.tex)
    #glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.cam.w, self.cam.h, self.tex_format, GL_UNSIGNED_BYTE, None)
    glTexSubImage2D(GL_TEXTURE_2D, 0, roix, roiy, roiw, roih, self.tex_format, GL_UNSIGNED_BYTE, None)

    [w,h]=self.shape()
    glBegin(GL_QUADS)
    x1=-(rect.x()-.5)*zoom
    y1=-(rect.y()-.5)*zoom
    #x2=x1+zoom*(self.cam.w) 
    x2=x1+zoom*w 
    #y2=y1+zoom*(self.cam.h)
    y2=y1+zoom*h
    glTexCoord2f(0, 0); glVertex3f(x1, y1, 0.)
    glTexCoord2f(1, 0); glVertex3f(x2, y1,  0.)
    glTexCoord2f(1, 1); glVertex3f(x2, y2, 0.)
    glTexCoord2f(0, 1); glVertex3f(x1, y2, 0.)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)

#  def preprocess(self):
#    d_raw=self.raw_pbo.d_map()
#    d_preproc=self.preproc_pbo.d_map()
#    libcudacam.tofloat(d_raw, d_preproc)
#    for filter in self.filters:
#      filter(d_preproc, d_preproc)
#    self.raw_pbo.d_unmap()
#    self.preproc_pbo.d_unmap()

  def tex_render(self, thres, vmin, vmax):
    self.glwidget.makeCurrent()
    d_tex=self.tex_pbo_inactive.d_map()
    #d_preproc=self.preproc_pbo.d_map()
    d_raw=self.raw_pbo.d_map()
    #libcudacam.float2gray(d_preproc, d_tex, ctypes.c_int(self.roi_size()), ctypes.c_int(thres), ctypes.c_int(vmin), ctypes.c_int(vmax))
    format=self.format()
    if format=="MONO12":
      libcudacam.uint16_to_gray8(d_raw, d_tex, ctypes.c_int(self.roi_size()), ctypes.c_int(thres), ctypes.c_int(vmin), ctypes.c_int(vmax))
    elif format=="MONO8":
      libcudacam.uint8_to_gray8(d_raw, d_tex, ctypes.c_int(self.roi_size()), ctypes.c_int(thres), ctypes.c_int(vmin), ctypes.c_int(vmax))
    elif format=="RGB8":
      [left,top,w,h]=self.roi()
      libcudacam.uint8_to_rgb8(d_raw, d_tex, ctypes.c_int(self.roi_size()), ctypes.c_int(w), ctypes.c_int(thres), ctypes.c_int(vmin), ctypes.c_int(vmax))
    self.tex_pbo_inactive.d_unmap()
    self.raw_pbo.d_unmap()
    #self.preproc_pbo.d_unmap()
    self.tex_pbo_idx=(self.tex_pbo_idx+1)%2
    self.tex_pbo_active=self.tex_pbo[self.tex_pbo_idx]
    self.tex_pbo_inactive=self.tex_pbo[(self.tex_pbo_idx+1)%2]

  def snap_to_raw_pbo(self):
    #self.raw_pbo_mutex.lock()
    #self.glwidget.makeCurrent()
    pbo=self.raw_pbo.h_map()
    self.snap(pbo)
    self.raw_pbo.h_unmap()
    #self.raw_pbo_mutex.unlock()

  def capture_to_raw_pbo(self):
    #self.raw_pbo_mutex.lock()
    #self.glwidget.makeCurrent()
    pbo=self.raw_pbo.h_map()
    self.capture(pbo)
    #f=self.capture()
    self.raw_pbo.h_unmap()
    #self.raw_pbo_mutex.unlock()

  def copy_to_raw_pbo(self, data):
    pbo=self.raw_pbo.h_map()
    ctypes.memmove(pbo, data.ctypes.data, data.nbytes)
    #f=self.capture()
    self.raw_pbo.h_unmap()
    #self.raw_pbo_mutex.unlock()

  def subarray(self, subx, suby, subw, subh):
    #self.raw_pbo_mutex.lock()
    #self.glwidget.makeCurrent()
    [x,y,w,h]=self.roi() #physical roi
    pbo=self.raw_pbo.h_map()
    data=zeros((subh, subw), dtype=world.camera.dtype())
    libcutils.memcpy_subarray(data.ctypes.data, pbo, 
      int(subx-x), int(suby-y), int(subw), int(subh),
      #self.cam.w, self.cam.bytesperpixel)
      w, self.raw_itemsize)
    self.raw_pbo.h_unmap()
    #self.raw_pbo_mutex.unlock()
    return data


