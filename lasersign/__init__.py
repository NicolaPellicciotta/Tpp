from PyQt4 import Qt, QtCore, QtGui, QtNetwork
import socket
import string
import siteconf


TCP_IP='141.108.1.20'
TCP_PORT=9999

class LaserLabel(QtGui.QLabel):
  def __init__(self, wavelength):
    super(LaserLabel, self).__init__()

    self.pixON=QtGui.QPixmap("pixmaps/%d-ON.png" % wavelength)
    self.pixOFF=QtGui.QPixmap("pixmaps/%d-OFF.png" % wavelength)

    self.setPixmap(self.pixOFF)
    self.ON=False


  def setON(self):
    self.setPixmap(self.pixON)
    self.ON=True

  def setOFF(self):
    self.setPixmap(self.pixOFF)
    self.ON=False

  def isON(self):
    return self.ON

class WarningLabel(QtGui.QLabel):
  def __init__(self):
    super(WarningLabel, self).__init__()

    self.setFont(QtGui.QFont("Arial", 100))
    self.setAlignment(QtCore.Qt.AlignCenter)
    self.setOFF()

  def setON(self):
    palette=QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Active,
                    QtGui.QPalette.WindowText, 
                    QtGui.QColor(255,0,0))

    self.setPalette(palette)
    self.setText("<b>LASERS ON!")

  def setOFF(self):
    palette=QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Active,
                    QtGui.QPalette.WindowText, 
                    QtGui.QColor(0,255,0))

    self.setPalette(palette)
    self.setText("<b>LASERS OFF")

  

class LaserPanelWidget(QtGui.QWidget):
  def __init__(self):
    super(LaserPanelWidget, self).__init__()

    self.WARNING=False

    self.warning=WarningLabel()
    self.hot=LaserLabel(532)
    self.dhm=LaserLabel(532)
    self.irt=LaserLabel(1064)
    self.tpp=LaserLabel(780)

    self.warning.setMaximumHeight(170)
    #self.hot.setMinimumWidth(700)
    #self.dhm.setMinimumWidth(700)
    #self.irt.setMinimumWidth(700)
    #self.tpp.setMinimumWidth(700)

    layout=QtGui.QGridLayout()
    layout.addWidget(self.warning,0,0,1,2)
    layout.addWidget(self.hot,1,0, Qt.Qt.AlignVCenter|Qt.Qt.AlignRight)
    layout.addWidget(self.dhm,2,0, Qt.Qt.AlignVCenter|Qt.Qt.AlignRight)
    layout.addWidget(self.irt,1,1, Qt.Qt.AlignVCenter|Qt.Qt.AlignLeft)
    layout.addWidget(self.tpp,2,1, Qt.Qt.AlignVCenter|Qt.Qt.AlignLeft)
    layout.setHorizontalSpacing(50)

    self.setLayout(layout)

    palette=QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Active,
                    QtGui.QPalette.Window, 
                    QtGui.QColor(0,0,0))
    self.setPalette(palette)



  def updateWarning(self):
    if any([laser.isON() for laser in [self.hot, self.dhm, self.irt, self.tpp]]):
      self.warning.setON()
    else:
      self.warning.setOFF()


class  LaserPanelServer(QtNetwork.QTcpServer):
  def __init__(self):
    super(LaserPanelServer, self).__init__()

    self.newConnection.connect(self.acceptConnection)

    self.panel=LaserPanelWidget()
    self.panel.show()

    self.listen(QtNetwork.QHostAddress.Any, TCP_PORT)

  def acceptConnection(self):
    print "New connection"
    self.client=self.nextPendingConnection()
    self.client.readyRead.connect(self.startRead)
    print self.client


  def startRead(self):
    msg=self.client.read(self.client.bytesAvailable())
    benchname, status=string.split(msg)
    if benchname == 'irt':
      bench=self.panel.irt
    elif benchname == 'tpp':
      bench=self.panel.tpp
    elif benchname == 'dhm':
      bench=self.panel.dhm
    elif benchname == 'hot':
      bench=self.panel.hot
    else:
      raise ValueError, "Unrecognized bench name"


    if status=='ON':
        bench.setON()
    else:
        bench.setOFF()

    self.panel.updateWarning()


class LaserPanelClient:
  def __init__(self, benchname):
    self.benchname=benchname

  def setON(self):
    self.send(self.benchname+" ON")    

  def setOFF(self):
    self.send(self.benchname+" OFF")    


  def send(self, msg):
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    sock.send(msg)    
    sock.close()


def laseron():
  c=LaserPanelClient(siteconf.hostname)
  c.setON()

def laseroff():
  c=LaserPanelClient(siteconf.hostname)
  c.setOFF()


