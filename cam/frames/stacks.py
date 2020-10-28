import zipfile
import numpy
from cStringIO import StringIO
from PyQt4 import QtCore, Qt, QtGui
from tiffio import *

app=Qt.QCoreApplication.instance()

def mkname(i):
  return "%0.9d.tiff" % i
 
class ZipStreamer(QtCore.QThread):
  def __init__(self, archive):
    super(ZipStreamer, self).__init__()
    self.archive=archive
    self.nsaved=0

  def run(self):
    self.archive.writestr(mkname(self.nsaved), self.datastring)
    self.nsaved+=1




class FrameStack(QtGui.QWidget):
  def __init__(self):
    super(FrameStack, self).__init__()

  def append(self, f):
    self._idx+=1
    self._time+=[f.time]
    self._frames+=[f]
    if len(self._frames)==1 and not self._streamer.isRunning():
      self.queue_frame()




  def queue_frame(self):
    #myprint("queuing")
    #myprint(str(len(self.frames)))
    #self.saved_bar.setValue(self.ciao.idx)
    if len(self._frames)>0:
      buf=StringIO()
      f=self._frames.pop(0)#.dumps()
      f.save(buf)
      self._streamer.datastring=buf.getvalue()
      #print "starting"
      self._streamer.start()

    nsaving=self._streamer.nsaved+1.
    if nsaving%5 == 0:
      self.progress_bar.setValue(100.*nsaving/self._idx)
      app.processEvents()





  def __getitem__(self, i):
    if i<0 or i>=self._idx:
      raise IndexError, "index out of bounds"
    buf=StringIO()
    buf.write(self._archive.read(mkname(i)))
    buf.seek(0)
    return loadframe(buf)

  def time(self):
    return numpy.array(self._time)

  def close(self):
    buf=StringIO()
    numpy.save(buf, self.time())
    self._archive.writestr("time.npy", buf.getvalue())
    self._archive.close()


def framestack(name, compress=False):
  """Create new stack for writing"""
  stack=FrameStack()
  stack._idx=0
  stack._time=[]
  stack._frames=[]

  if compress:
    compression=zipfile.ZIP_DEFLATED
  else:
    compression=zipfile.ZIP_STORED

  stack._archive=zipfile.ZipFile(name, mode="w", compression=compression, allowZip64=True)

  layout=QtGui.QGridLayout()
  stack.setLayout(layout)

  stack.progress_bar=QtGui.QProgressBar()
  stack.progress_bar.setMaximum(100)
  label=QtGui.QLabel("Streaming rate:")
  layout.addWidget(label,1,1)
  layout.addWidget(stack.progress_bar,1,2)
  stack.show()

  stack._streamer=ZipStreamer(stack._archive)
  stack.connect(stack._streamer, QtCore.SIGNAL("finished()"),  stack.queue_frame)



  return stack


def loadstack(name):
  """Open existing stack in read only mode"""
  stack=FrameStack()
  stack._archive=zipfile.ZipFile(name, mode="r", allowZip64=True)
  stack._idx=len(stack._archive.namelist())-1 #there's  1 time.npy file

  buf=StringIO()
  buf.write(stack._archive.read("time.npy"))
  buf.seek(0)
  stack._time=numpy.load(buf)
 
 
  return stack
