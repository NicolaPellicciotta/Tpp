import ctypes
import numpy
from numpy import *
import time
from ppmio import *
import atexit
#import world

#from Tkinter
#import Tkinter as Tk
#import tkFont

#from PIL
#from PIL import Image, ImageTk



#libcam=ctypes.cdll.LoadLibrary('libgige.dylib')
#libcam=ctypes.cdll.LoadLibrary('libcam.so')
#libcam=ctypes.cdll.LoadLibrary('libdcam.so')

CAMATTRS=["shutter", "gain", "model", "roi", "size"]

class CamError(Exception):
  """Raised when a libcam function returns with an error status

  Attributes:
    fname -- function name
  """
  def __init__(self, msg, code=None):
    self.msg=msg.value
    self.code=code
  def __str__(self):
    if not self.code:
      return self.msg
    else:
      return self.msg+" code: %d" % self.code

#Clean up 

#def cleanup():
# if world.ccd is not None:
#   world.ccd.__del__()

#atexit.register(cleanup)

#======================================
#   gigecam class
#======================================
class Orca:
  empty=array([], uint8)
  w=1920
  h=1336
  dtype=uint16
  def __init__(self):
    self._STREAMING=False
    self._roi=[0,0,1920,1336]
    self.bytesperpixel=self.dtype(0).itemsize
    self._frame=load("/home/roberto/Documents/Dev/Python/holocam/cameras/hamamatsu_emul/frame.npy")

  def shutter(self,val=None):
    if self._STREAMING:
      ErrMsg.value="Cannot set cam attributes while streaming"
      raise CamError(ErrMsg)

    if val:
      self._shutter=val
    else:
      return self._shutter

  def roi(self,val=None):
    if self._STREAMING:
      ErrMsg.value="Cannot set cam attributes while streaming"
      raise CamError(ErrMsg)

    if val:
      self._roi=val
    else:
      return self._roi


  def snap(self, bufp=None):
    RETURNS=False
    if self._STREAMING:
      ErrMsg.value="Cannot snap while streaming"
      raise CamError(ErrMsg)

    [w,h]=self._roi[2:]
    if bufp==None:
      RETURNS=True
      buf=numpy.zeros((h,w), dtype=self.dtype)
      bufp=buf.ctypes.data

    #noise=random.random_integers(0,400, size=(100,100)).astype(self.dtype)
    #noise=tile(noise,(14,20))[:1336, :1920]
    frame=self._frame#+noise

    ctypes.memmove(bufp, frame.ctypes.data, w*h*self.bytesperpixel)
    timestamp=0

    if RETURNS:
      if status==0:
        return frame(buf, timestamp.value, 0)
      else:
        return frame(camera.empty, timestamp.value, 0, status)
