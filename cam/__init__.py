from PyQt4 import QtCore, QtGui, Qt
from qt import *
from frames import *
import world
import siteconf
import time
import video

def camcleanup():
    if world.ccd is not None:
        world.ccd.view.glcam.__del__()

#atexit.register(camcleanup)

ICONPATH="/home/roberto/Documents/Dev/Python/cam/icons/"

app=Qt.QCoreApplication.instance()

class StackBrowser(QtGui.QWidget):
  def __init__(self, view):
    super(StackBrowser, self).__init__()

    self.slider=QtGui.QSlider()
    self.slider.setMinimum(0)
    self.slider.setSingleStep(1)
    self.slider.setOrientation(QtCore.Qt.Horizontal)
    self.slider.valueChanged.connect(self.showframe)
    layout=QtGui.QHBoxLayout()
    layout.addWidget(self.slider)
    self.setLayout(layout)
    self.view=view

  def load(self, filename):
    self.stack=loadstack(filename)
    self.slider.setMaximum(self.stack._idx-1)
   
  def showframe(self, i):
    data=self.stack[i].data
    self.view.load_frame(data)
    self.view.scene().update()



class camera(QtGui.QWidget):

  def __init__(self, parent=None):
    #if world.camera:
    #  raise Exception( "There is an open camera in the world")

    super(camera, self).__init__(parent)
    self.view=CamView()

    world.scene=self.view.scene()
    world.ccd=self

    #Setup toolbar
    toolbar=QtGui.QToolBar()
    toolbar.setIconSize(QtCore.QSize(32,32))
    self.play_action=QtGui.QAction(QtGui.QIcon(ICONPATH+"button_black_play.png"), 
        "Start preview", self, triggered=self.play, enabled=True)
    #self.pause_action=QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaPause), 
    self.pause_action=QtGui.QAction(QtGui.QIcon(ICONPATH+"button_black_pause.png"), 
        "Stop preview", self, triggered=self.pause, enabled=False)
    self.rec_action=QtGui.QAction(QtGui.QIcon(ICONPATH+"button_black_rec.png"), 
        "Toggle Record", self, triggered=self.record, enabled=True)
    toolbar.addAction(self.play_action)
    toolbar.addAction(self.pause_action)
    toolbar.addAction(self.rec_action)
    toolbar.addSeparator()

    #Layout
    layout=QtGui.QVBoxLayout()
    layout.addWidget(toolbar)
    layout.addWidget(self.view)
    self.setLayout(layout)

    self.show()
    self.view.fitInView(self.view.proi, QtCore.Qt.KeepAspectRatio)
    self.view.update_scene_exposure()

    #Signals
    #self.refreshed=QtCore.pyqtSignal()
    self.stackbrowser=StackBrowser(self.view)

    #Timing
    self.timer=QtCore.QTimer()
    self.timer.timeout.connect(self.refresh)
    self.timer.setSingleShot(True)
    self._PREVIEWING=False
    self._RECORDING=False
    self._dt=20
    self.setGeometry(QtCore.QRect(953, 52, 964, 1001))
    self.play()

  def __del__(self):
    print 'del ccd'
    self.pause()
    #self.view.glcam.__del__()

  def closeEvent(self,event):
    print 'closeEvent'
    #self.view.glcam.__del__()
    #self.deleteLater()
    event.accept()
    #self.__del__()

  def sizeHint(self):
    return QtCore.QSize(1280,1024)

  def play(self):
    if self.play_action.isEnabled():
      self._PREVIEWING=True
      self.timer.start(self._dt)
      self.play_action.setEnabled(False)
      self.pause_action.setEnabled(True)

  def pause(self):
    if self.pause_action.isEnabled():
      self._PREVIEWING=False
      self.pause_action.setEnabled(False)
      self.play_action.setEnabled(True)

  def record(self):
    if self._RECORDING:
      self.video.close()
      self._RECORDING=False
      self.rec_action.setIcon(QtGui.QIcon(ICONPATH+"button_black_rec.png"))
    else:
      w,h=self.view.proi._w, self.view.proi._h
      self.video=video.Video(w, h)
      self._RECORDING=True
      self.rec_action.setIcon(QtGui.QIcon(ICONPATH+"button_red_rec.png"))
 
  def stream(self):
    self.view.glcam.stream()

  def stop(self):
    self.view.glcam.stop()

  def capture(self):
    return self.view.glcam.capture()

  def snap(self):
    return self.view.glcam.snap()

  def shutter(self, val=None):
    return self.view.glcam.shutter(val)

  def framerate(self, val=None):
    return self.view.glcam.framerate(val)

  def gain(self, val=None):
    retval=self.view.glcam.gain(val)
    if val is None:
      return retval
  
  def cps(self):
    return self.view.glcam.cps()

  def mpp(self):
    return self.view.glcam.mpp()

  def dtype(self):
    return self.view.glcam.dtype()

  def shape(self):
    return self.view.glcam.shape()

  def format(self, val=None):
    retval=self.view.glcam.format(val)
    if val is None:
      return retval
    else:
      datatype=self.view.glcam.dtype()
      if datatype==uint8: vmax=255
      elif datatype==uint16: vmax=4095
      self.view.limits(0, vmax)

  def limits(self, vmin=None, vmax=None):
    self.view.limits(vmin, vmax)

  def thres(self, val):
    self.view.thres(val)

  def roi(self, roi=None):
    if roi is None:
      return self.view.glcam.roi()
    else:
      self.view.glcam.roi(roi)
      self.view.proi.roi(self.view.glcam.roi())

  def resetRoi(self):
    ccdshape=self.view.glcam.shape()
    roi=[0,0,ccdshape[0],ccdshape[1]]
    self.view.glcam.roi(roi)
    self.view.proi.roi(self.view.glcam.roi())    

  def add_roi(self, pos=None):
    roi=VirtualRoiItem(pos=pos)
    self.view.scene().clearSelection()
    self.view.scene().addItem(roi)
    return roi

  def gcr(self):
    return self.view.scene().gcr()

  def refresh(self, data=None):
    #if self._PREVIEWING and self.view.glcam.isstreaming():
    if data is None:
      self.view.get_frame()
      self.view.scene().update()
    else:
      self.view.load_frame(data)
      self.view.scene().update()
      app.processEvents()
    
    #  self.refreshed.emit()
    #  for item in self.scene().items():
    #  if isinstance(item, VirtualRoiItem):
    #    item.crop()
        #item.data=self.get_subarray(item)

    #update monitors
      #for m in monitor.active():
      #  m.update()

    if self._RECORDING:
      self.video.append(self.view.glcam.subarray(self.view.proi.x(),self.view.proi.y(), self.view.proi._w, self.view.proi._h))

    if self._PREVIEWING:
      self.timer.start(self._dt)#TODO: check loop  

  def checkfps(self):
    stopped=False
    if self._PREVIEWING:
      self.pause()
      time.sleep(1)
      stopped=True

    try:
      self.stream()
      t=[]
      for i in range(100):
        f=self.capture()
        t+=[f.time]
      self.stop()
      t=array(t)
      dt=diff(t)/self.cps()
      av=mean(dt)
      sd=std(dt)
      print 
      print "fps: %.1f" % (1./av)
      print "dt: %.1e +/- %.1e(%.1e)" % (av,sd,sd/av)
      #print "dt: %e +/- %e(%e)" % (av,sd,sd/av)
      print "max rel fluctuation: %.1e" % (max(abs(dt-av))/av)

    except CamError, e:
      print e.msg

    if stopped:
      self.play()

  def recvid(self,Nframes,fps):
    self.pause()
    self.framerate(fps)
    t=[]    #list for frametimes:
    w,h=self.view.proi._w, self.view.proi._h
    self.vid=video.Video(w,h,fps=fps)    
    self.stream()
    for i in range(Nframes):
        f=self.capture()
        self.vid.append(f.data)
        t+=[f.time]
    self.stop()
    dt=(diff(array(t))/self.cps())    
    fps_real=round(1./dt.mean())
    print "fps achieved: " + str(fps_real)    
    self.vid.close()

  def load(self, filename):
    self.stackbrowser.load(filename)
    self.stackbrowser.show()
    self.pause()










