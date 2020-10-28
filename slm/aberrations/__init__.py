import world
from PyQt4 import Qt, QtCore, QtGui
#from form import Ui_Form
from zernike import Ui_Form
from tweezers import *
from scipy.optimize import  fmin_powell
import string
import numpy

app=Qt.QCoreApplication.instance()

def processQtEvents(*args):
  app.processEvents()

class AberrationsWidget(QtGui.QWidget):
  def __init__(self,h_ref=None):
    super(AberrationsWidget, self).__init__()
    self.ui=Ui_Form()
    self.ui.setupUi(self)

    if world.slm.aberration==None:
        print 'removing previous aberration'
        world.slm.aberration

    if h_ref==None:
        t=trap(-15,0)
        self.h=holo(t)
    else:
        self.h=h_ref.copy()
    world.slm.show(self.h)

    w,h=world.slm.width, world.slm.height
    J,I=indices((h, w), dtype=float)
    self.X=(I-w/2)/(w/2)
    self.Y=(J-h/2)/(w/2)
    self.rho=sqrt(self.X**2+self.Y**2)
    self.theta=arctan2(self.X, self.Y)

    self.defocus=sqrt(3)*(2*self.rho**2-1)
    self.astigx=sqrt(6)*(self.rho**2)*sin(2*self.theta)
    self.astigy=sqrt(6)*(self.rho**2)*cos(2*self.theta)
    self.comam=sqrt(8)*(3*self.rho**3-2*self.rho)*sin(self.theta)
    self.comap=sqrt(8)*(3*self.rho**3-2*self.rho)*cos(self.theta)
    self.trefoilm=sqrt(8)*(self.rho**3)*sin(3*self.theta)
    self.trefoilp=sqrt(8)*(self.rho**3)*cos(3*self.theta)
    self.spherical=sqrt(5)*(6*self.rho**4-6*self.rho**2+1)

    self.ui.applyButton.clicked.connect(self.apply)
    self.ui.fitButton.clicked.connect(self.fit)
    self.ui.saveButton.clicked.connect(self.filedialog)

    self.show()

  def apply(self):
    world.slm.show(self.h+self.aberr())

  def getparam(self, parMin, parMax, parSlider):
    minval=parMin.value()
    maxval=parMax.value()
    return minval+(maxval-minval)*parSlider.value()/100.
 
  def aberr(self):
    ab=zeros_like(self.h)
    if self.ui.defocusCheck.isChecked():
      ampl=self.getparam(self.ui.defocusMin, self.ui.defocusMax, self.ui.defocusSlider)
      ab+=ampl*self.defocus
    if self.ui.astigxCheck.isChecked():
      ampl=self.getparam(self.ui.astigxMin, self.ui.astigxMax, self.ui.astigxSlider)
      ab+=ampl*self.astigx
    if self.ui.astigyCheck.isChecked():
      ampl=self.getparam(self.ui.astigyMin, self.ui.astigyMax, self.ui.astigySlider)
      ab+=ampl*self.astigy
    if self.ui.comamCheck.isChecked():
      ampl=self.getparam(self.ui.comamMin, self.ui.comamMax, self.ui.comamSlider)
      ab+=ampl*self.comam
    if self.ui.comapCheck.isChecked():
      ampl=self.getparam(self.ui.comapMin, self.ui.comapMax, self.ui.comapSlider)
      ab+=ampl*self.comap
    if self.ui.trefoilmCheck.isChecked():
      ampl=self.getparam(self.ui.trefoilmMin, self.ui.trefoilmMax, self.ui.trefoilmSlider)
      ab+=ampl*self.trefoilm
    if self.ui.trefoilpCheck.isChecked():
      ampl=self.getparam(self.ui.trefoilpMin, self.ui.trefoilpMax, self.ui.trefoilpSlider)
      ab+=ampl*self.trefoilp
    if self.ui.sphericalCheck.isChecked():
      ampl=self.getparam(self.ui.sphericalMin, self.ui.sphericalMax, self.ui.sphericalSlider)
      ab+=ampl*self.spherical
    return ab


  def fit(self):
    self.ui.fitButton.setEnabled(False)
    self.ui.fitButton.setEnabled(True)


  def filedialog(self):
    self.d=QtGui.QFileDialog()
    self.d.fileSelected.connect(self.save)
    self.d.show()

  def save(self, filename):
    numpy.save(str(filename), self.aberr())



 
