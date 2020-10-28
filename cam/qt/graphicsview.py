from PyQt4 import QtCore, QtGui
import world
import numpy as np
from cam.opengl import *

corners=[TopLeftCorner, TopRightCorner, BottomRightCorner, BottomLeftCorner]=range(4)
edges=[RightEdge, LeftEdge, TopEdge, BottomEdge] = range(4,8)
Origin=8

def dist(p1, p2):
  return QtCore.QLineF(p1, p2).length()

class BaseRoiItem(QtGui.QGraphicsItem):
  font=QtGui.QFont("Helvetica", pointSize=12, weight=100)

  def __init__(self, w, h, pos):
    super(BaseRoiItem, self).__init__()
    self.pen1=QtGui.QPen(QtGui.QColor(255,255,  0,150), 3)
    self.pen2=QtGui.QPen(QtGui.QColor(255,255,  0,255), 3)

    self._w=w
    self._h=h
    self.setPos(pos)

    self._handle=None

    self.setAcceptHoverEvents(True)
    self.setFlags(QtGui.QGraphicsItem.ItemIsFocusable|
                  QtGui.QGraphicsItem.ItemIsSelectable)


  def roi(self, roi=None):
    if roi is not None:
      [x,y,w,h]=roi
      self.setPos(QtCore.QPointF(x,y))
      self._w=w
      self._h=h
    else:
      return [int(self.x()), int(self.y()), int(self._w), int(self._h)]

  def find_corner(self, pos):
    rect=QtCore.QRectF(0,0,self._w, self._h)
    R=20.
    if dist(pos, rect.topLeft())<R:
      return TopLeftCorner
    elif dist(pos, rect.topRight())<R:
      return TopRightCorner
    elif dist(pos, rect.bottomLeft())<R:
      return BottomLeftCorner
    elif dist(pos, rect.bottomRight())<R:
      return BottomRightCorner
    else:
      return None

  def find_edge(self, pos):
    rect=QtCore.QRectF(0,0,self._w, self._h)
    R=20.
    if abs(pos.x()-rect.right())<R:
      return RightEdge
    if abs(pos.x()-rect.left())<R:
      return LeftEdge
    if abs(pos.y()-rect.top())<R:
      return TopEdge
    if abs(pos.y()-rect.bottom())<R:
      return BottomEdge
    else:
      return None

  def boundingRect(self):
    lw=self.pen1.width()
    return QtCore.QRectF(0, 0, self._w, self._h).adjusted(-lw,-lw,lw,lw)

  def shape(self):
    """Define shape so that item only grabs mouse events from within roi's pixels"""
    path=QtGui.QPainterPath()
    #qrect width is defined as x2-x1
    #so it's 1 pixel larger then the actual number of spanned pixels
    path.addRect(QtCore.QRectF(0, 0, self._w-1, self._h-1))
    return path

  def hoverMoveEvent(self, event):
    #super(RoiItem, self).hoverMoveEvent(event)
    corner=self.find_corner(event.pos())
    edge=self.find_edge(event.pos())
    if corner==TopLeftCorner or corner==BottomRightCorner:
      self.setCursor(QtCore.Qt.SizeFDiagCursor)
    elif corner==TopRightCorner or corner==BottomLeftCorner:
      self.setCursor(QtCore.Qt.SizeBDiagCursor)
    elif edge==RightEdge or edge==LeftEdge:
      self.setCursor(QtCore.Qt.SizeHorCursor)
    elif edge==TopEdge or edge==BottomEdge:
      self.setCursor(QtCore.Qt.SizeVerCursor)
    else: 
      self.setCursor(QtCore.Qt.ArrowCursor)

  def mousePressEvent(self, event):
    corner=self.find_corner(event.pos())
    edge=self.find_edge(event.pos())
    if event.button() == QtCore.Qt.LeftButton:
      if corner is not None:
        self._handle=corner
      elif edge is not None:
        self._handle=edge
    #else:
    #  super(BaseRoiItem, self).mousePressEvent(event)

  def mouseMoveEvent(self, event):
    if self._handle in corners+edges:
      self.resize_roi(event)
    elif self.isSelected():
      delta=event.pos()-event.lastPos()
      self.moveBy(round(delta.x()), round(delta.y()))


  def mouseReleaseEvent(self, event):
    if self._handle is not None:
      self._handle=None
    
    super(BaseRoiItem, self).mouseReleaseEvent(event)


  def resize_roi(self, event):
    newpos=self.pos()
    #round to closest pixel
    x,y=round(event.pos().x()), round(event.pos().y())

    #calculate new shape
    if self._handle==TopLeftCorner:
      wnew=self._w-x
      hnew=self._h-y

    elif self._handle==TopRightCorner:
      wnew=x
      hnew=self._h-y

    elif self._handle==BottomLeftCorner:
      wnew=self._w-x
      hnew=y

    elif self._handle==BottomRightCorner:
      wnew=x
      hnew=y

    elif self._handle==RightEdge:
      wnew=x
      hnew=self._h

    elif self._handle==LeftEdge:
      wnew=self._w-x
      hnew=self._h

    elif self._handle==TopEdge:
      wnew=self._w
      hnew=self._h-y

    elif self._handle==BottomEdge:
      wnew=self._w
      hnew=y

    #snap to multiples of 8
    if event.modifiers() & QtCore.Qt.ShiftModifier:
      wnew=round(wnew/8.)*8.
      hnew=round(hnew/8.)*8.

    #move pos if needed
    if self._handle in [BottomLeftCorner, TopLeftCorner] or self._handle==LeftEdge:
      newpos.setX(newpos.x()+self._w-wnew)

    if self._handle in [TopLeftCorner, TopRightCorner] or self._handle==TopEdge:
      newpos.setY(newpos.y()+self._h-hnew)

    #apply changes
    [camwidth, camheight]=world.camera.shape()
    if wnew>64 and wnew<=camwidth and hnew>64 and hnew<=camheight:
      self._w=round(wnew)
      self._h=round(hnew)
      self.origin=QtCore.QPointF(round(self._w/2.), round(self._h/2.))
      self.setPos(newpos)
      #self.update()


  def paint(self, painter, option, widget):
    if self.isSelected():
      pen=self.pen2
    else:
      pen=self.pen1

    painter.setPen(pen)
    painter.drawRect(-1,-1,self._w+3,self._h+3) #pen draws outline, all pixels in roi are visible
    painter.setFont(self.font)
    textwidth=100
    painter.drawText(QtCore.QRectF(self._w/2.-textwidth/2.,-24, textwidth, 18),
                     QtCore.Qt.AlignHCenter,  "%d, %d" % (self._w, self._h))
 

class Target:

  def __init__(self,x,y,r,label):
    self.x=x
    self.y=y
    self.r=r
    self.label=label
    self.pen=QtGui.QPen(QtGui.QColor(0,255,0, 50), 3)

  def paint(self, painter):
    painter.setPen(self.pen)
    painter.drawEllipse(self.x-self.r, self.y-self.r, 2*self.r, 2*self.r)

    if self.label:
      textwidth=100
      d=self.r/np.sqrt(2)
      painter.drawText(QtCore.QRectF(self.x+d, self.y-d-18, textwidth , 18),
                     QtCore.Qt.AlignLeft,  self.label)


class VirtualRoiSignals(QtCore.QObject):
  #Signal implementation requires direct subclassing from QObject
  #but multiple inheritance id forbidden in pyqt
  refreshed=QtCore.pyqtSignal()
  def __init__(self):
    super(VirtualRoiSignals, self).__init__()

class VirtualRoiItem(BaseRoiItem):

  def __init__(self, pos=None):
    self.pen3=QtGui.QPen(QtGui.QColor(255,255,255, 50), 3)
    self.pen4=QtGui.QPen(QtGui.QColor(255,255,255, 150), 3)

    w=300
    h=300
    if pos is None:
      pos=QtCore.QPointF(100., 100.)
    
    super(VirtualRoiItem, self).__init__(w,h,pos-QtCore.QPointF(w/2., h/2.))
    self.data=None
    self.origin=QtCore.QPointF(self._w/2., self._h/2.)
    self.setSelected(True)

    self.targets=[]
    #Signals
    self.signals=VirtualRoiSignals()

    self.show()


  def on_origin(self, pos):
    rect=QtCore.QRectF(0,0,self._w, self._h)
    R=20.
    if dist(pos, self.origin)<R:
      return True
    else:
      return False

  def hoverMoveEvent(self, event):
    if self.on_origin(event.pos()):
      self.setCursor(QtCore.Qt.CrossCursor)
    else: 
      super(VirtualRoiItem, self).hoverMoveEvent(event)

  def mousePressEvent(self, event):

    if self.on_origin(event.pos()):
      self._handle=Origin
#      self.update() #TODO check if needed
    else: 
      super(VirtualRoiItem, self).mousePressEvent(event)

  def mouseMoveEvent(self, event):
    if self._handle==Origin:
      x,y=round(event.pos().x()), round(event.pos().y())
      if self.contains(event.pos()):
        self.origin=QtCore.QPointF(x,y) 
        #self.update()
    else: 
      super(VirtualRoiItem, self).mouseMoveEvent(event)

  def crop(self):
    #self.data=np.zeros((self._h, self._w), dtype=world.camera.dtype())
    #self.scene().glcam.subarray(self.data, self.x(), self.y(), self._w, self._h)
    self.data=self.scene().glcam.subarray(self.x(), self.y(), self._w, self._h)

  def slice(self):
    proi=self.scene().views()[0].proi
    roix=self.x()-proi.x()
    roiy=self.y()-proi.y()
    return [slice(int(roiy), int(roiy+self._h)), slice(int(roix), int(roix+self._w))]

  def target(self, x, y, r=10, label=None):
   
    if len(x)==1:
      self.targets=[Target(x,y,r,label)]
    else:
      self.targets=map(lambda a,b: Target(a,b,r,label),x,y)


  def paint(self, painter, option, widget):
    super(VirtualRoiItem, self).paint(painter, option, widget)
    painter.setPen(self.pen3)
    painter.drawLine(QtCore.QPointF(self.origin.x(),1), QtCore.QPointF(self.origin.x(), self._h-2))
    painter.drawLine(QtCore.QPointF(1, self.origin.y()), QtCore.QPointF(self._w-2, self.origin.y()))

    for t in self.targets:
      t.paint(painter)
 
    painter.setPen(self.pen4)
    painter.drawText(4, self.origin.y()-6,"%d" % self.origin.y())
    painter.rotate(90)
    #painter.translate(QtCore.QPointF(0,-self._w))
    painter.drawText(4, -self.origin.x()-6,"%d" % self.origin.x())

     
class PhysicalRoiItem(BaseRoiItem):
  def __init__(self, pos=None):
    [w,h]=world.camera.shape()
    pos=QtCore.QPointF(0., 0.)
    super(PhysicalRoiItem, self).__init__(w,h,pos)
    self.pen1=QtGui.QPen(QtGui.QColor(0,255,  0,150), 3)
    self.pen2=QtGui.QPen(QtGui.QColor(0,255,  0,255), 3)

    self.show()
 
class CamScene(QtGui.QGraphicsScene):
  def __init__(self, glcam, parent=None):
    super(CamScene, self).__init__(parent)
    self.glcam=glcam
    margin=100
    #self.setSceneRect(-margin, -margin, glcam.cam.w+2*margin, glcam.cam.h+2*margin)
    [w,h]=self.glcam.shape()
    self.setSceneRect(-margin, -margin, w+2*margin, h+2*margin)
    self.exposed_rect=None
    self.zoom=1

  def gcr(self):
    items=self.selectedItems()
    if len(items) == 1 and isinstance(items[0], VirtualRoiItem):
      return items[0]

  def update_exposure(self, rect, zoom):
    self.exposed_rect=rect
    self.zoom=zoom

  def drawBackground(self, painter, rect):
    painter.beginNativePainting()
    self.glcam.paintgl(self.exposed_rect, self.zoom)
    painter.endNativePainting()

  def mouseDoubleClickEvent(self, event):
    pos=event.scenePos()
    pos.setX(round(pos.x()))
    pos.setY(round(pos.y()))
    roi=VirtualRoiItem(pos)
    self.clearSelection()
    self.addItem(roi)

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Delete:
      for item in self.selectedItems():
        if isinstance(item, VirtualRoiItem):
          self.removeItem(item)
      

class CamView(QtGui.QGraphicsView):

  def __init__(self, parent=None):
    super(CamView, self).__init__(parent)

    self.glcam=CudaGLCam()
    self.zoom=1
    self._SCROLLING=False
    if self.glcam.dtype()==uint8:
      vmax=255
    elif self.glcam.dtype()==uint16:
      vmax=4095

    self._vmin=0
    self._vmax=vmax
    self._thres=0


    #Qt conf
    self.setRenderHint(QtGui.QPainter.Antialiasing)
    self.setViewport(self.glcam.glwidget)
    self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
    #direct scrolling using scrollbar dezctivated by now
    self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    #set scene
    self.setScene(CamScene(self.glcam))
    self.update_scene_exposure()

    self.proi=PhysicalRoiItem()
    self.scene().addItem(self.proi)



  def update_scene_exposure(self):
    zoom=self.transform().m11()
    rect=QtCore.QRectF(self.mapToScene(0,0), self.mapToScene(self.width(), self.height()))
    self.scene().update_exposure(rect, zoom)


  def limits(self, vmin=None, vmax=None):
    if vmin:
      self._vmin=vmin

    if vmax:
      self._vmax=vmax

  def thres(self, val):
    self._thres=val

  def get_frame(self):
    #self.glcam.capture_to_raw_pbo()
    self.glcam.snap_to_raw_pbo()

    #self.glcam.preprocess()
    self.glcam.tex_render(self._thres, self._vmin, self._vmax)

    for item in self.scene().items():
      if isinstance(item, VirtualRoiItem):
        item.crop()
        item.signals.refreshed.emit()

  def load_frame(self, data):
    #self.glcam.capture_to_raw_pbo()
    self.glcam.copy_to_raw_pbo(data)

    #self.glcam.preprocess()
    self.glcam.tex_render(self._thres, self._vmin, self._vmax)

    for item in self.scene().items():
      if isinstance(item, VirtualRoiItem):
        item.crop()
        item.signals.refreshed.emit()


  def resizeEvent(self, event):
    super(CamView, self).resizeEvent(event)
    self.update_scene_exposure()

  #def scrollContentsBy(self, dx, dy):
  #  super(CamView, self).scrollContentsBy(dx,dy)
  #  self.update_scene_exposure()

  def scale(self, sx, sy):
    self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
    super(CamView, self).scale(sx,sy)
    self.update_scene_exposure()

  def translate(self, dx, dy):
    self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
    super(CamView, self).translate(dx,dy)
    self.update_scene_exposure()

  def wheelEvent(self, event):
    s=2.**(event.delta()/1000.)
    self.scale(s,s)

  def mousePressEvent(self, event):
    if event.button()==QtCore.Qt.RightButton:
      self._SCROLLING=True
      self._lastpos=event.pos()
    else:
      super(CamView, self).mousePressEvent(event)
 
  def mouseReleaseEvent(self, event):
    if event.button()==QtCore.Qt.RightButton:
      self._SCROLLING=False
    else:
      super(CamView, self).mouseReleaseEvent(event)
 
  def mouseMoveEvent(self, event):
    if self._SCROLLING:
      pos=event.pos()
      zoom=self.transform().m11()
      delta=pos-self._lastpos
      self._lastpos=pos
      self.translate(delta.x()/zoom,delta.y()/zoom)
    else:
      super(CamView, self).mouseMoveEvent(event)
      #self.update_scene_exposure()

  def keyPressEvent(self, event):
    if event.key()==QtCore.Qt.Key_Return:
      self.glcam.roi(self.proi.roi())
      self.proi.roi(self.glcam.roi())
    else:
      super(CamView, self).keyPressEvent(event)

  def focusInEvent(self, event):
    #restores Override Cursor set by matplotlib
    QtGui.QApplication.restoreOverrideCursor()
    super(CamView, self).focusInEvent(event)






