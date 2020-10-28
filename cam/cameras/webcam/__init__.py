import ctypes

#import cv
from numpy import  *

class Webcam:
  def __init__(self):
    self._capture=cv.CaptureFromCAM(0)
    self.w=int(cv.GetCaptureProperty(self._capture, cv.CV_CAP_PROP_FRAME_WIDTH))
    self.h=int(cv.GetCaptureProperty(self._capture, cv.CV_CAP_PROP_FRAME_HEIGHT))
    self.dtype=uint8


  def snap(self):
    f=cv.QueryFrame(self._capture)
    data=fromstring(f.tostring(), dtype=self.dtype).reshape((self.h, self.w, 3))
    return data

  def snaptobuf(self, buf):
    f=cv.QueryFrame(self._capture)
    data=array(fromstring(f.tostring(), dtype=self.dtype).reshape((self.h, self.w, 3))[:,:,0])
    ctypes.memmove(buf, data.ctypes.data, data.size) 
