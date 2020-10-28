import PIL
from PIL import Image
import pickle
from numpy import fromstring,uint8, uint16

def tiffsave(filename, data, info=None):
  [h,w]=data.shape
  if data.dtype == uint8:
    mode="L"
  elif data.dtype == uint16:
    mode="I;16"
    data=data*16 #rescaling to full 16bit for previewing in os 


  img=Image.fromarray(data, mode=mode)

  if info:
    options={"description": pickle.dumps(info)} #goes in tag 270
    img.save(filename, format="TIFF", **options)
  else:
    img.save(filename, format="TIFF")

def tiffload(filename):
  img=Image.open(filename)
  if img.mode == "L":
    datatype=uint8
  elif img.mode == "I;16":
    datatype=uint16
  data=fromstring(img.tostring(), datatype)
 
  if img.mode == "I;16":
    data=data/16 #rescaling to 12bit 
  
  [w,h]=img.size
  data=data.reshape((h,w))

  info=pickle.loads(img.tag[270]) #tag 270 is for description

  return [data, info]

class frame:
  def __init__(self, data, time, origin, comments=""):
    self.data=data.copy()
    self.time=time
    self.origin=origin
    self.comments=comments

  def __repr__(self):
    str="frame object:\n\n"
    str+="\troi:\t\t(%d,%d,%d,%d)\n" % (tuple(self.origin)+tuple(self.data.shape))
    str+="\ttimestamp:\t%d\n" % self.time
    str+="\tcomments:\t%s" % self.comments
    return str

  def save(self, filename, comments=""):
    self.comments=comments
    info={"time": self.time, "origin" : self.origin, "comments": self.comments}
    tiffsave(filename, self.data, info=info)

def loadframe(filename):
  [data, info]=tiffload(filename)
  return frame(data, info["time"], info["origin"], info["comments"])

