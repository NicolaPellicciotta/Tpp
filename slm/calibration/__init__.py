from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
from numpy import *
import siteconf
import world

from PyQt4.Qwt5 import *

class alignWidget(QtGui.QWidget):
    def __init__(self, h_ref):
        super(alignWidget, self).__init__()
        layout=QtGui.QVBoxLayout(self)
        self.infotext=QtGui.QLabel(parent=self)
        #inftext=QtCore.QString("<P><b><FONT COLOR='#ff0000' FONT SIZE = 4>")
        #inftext.append("Use the keyboard arrow keys\n to shift the hologram")
        #inftext.append("</b></P></br>")
        #self.infotext.setText(inftext)
        self.infotext.setWordWrap(True)
        self.infotext.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.infotext)

        self.shifttext=QtGui.QLabel(parent=self)
        self.shifttext.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.shifttext)
        self.setLayout(layout)
        self.setGeometry(50,50,350,200)
        self.show()

        world.slm.slm_shift=[0,0]
        world.slm.show(h_ref)
        self.h_ref=h_ref.copy()

    #override the default keyboard event callback:
    def keyPressEvent(self, event):

        if event.key()==QtCore.Qt.Key_Left:
            world.slm.slm_shift[1]-=1            
        elif event.key()==QtCore.Qt.Key_Right:
            world.slm.slm_shift[1]+=1          
        elif event.key()==QtCore.Qt.Key_Up:
            world.slm.slm_shift[0]+=1          
        elif event.key()==QtCore.Qt.Key_Down:
            world.slm.slm_shift[0]-=1  
        else:
            return QtGui.QWidget.keyPressEvent(self, event)

        world.slm.show(self.h_ref)
        #shtext=QtCore.QString("<P><b><FONT COLOR='#1111C7' FONT SIZE = 8>")
        #shtext.append('pixelshifts:\t' + str(world.slm.xshift) + 'x\t' +  str(world.slm.yshift) + 'y')
        #shtext.append("</b></P></br>")
        #self.shifttext.setText(shtext)

