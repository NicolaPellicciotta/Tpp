import time
from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL import GL, GLU
from scipy.interpolate import splrep, splev


DEFAULT_SPEED=10
DEFAULT_TIMEBASE=1.e-3

class Stroke:
    def __init__(self, nodes, speedfactor=1, order=1):
        self.nodes=array(nodes)
        self.speedfactor=speedfactor
        self.order=order

    def nodeCoords(self):
        return self.nodes

    def pathCoords(self, speed, timebase):
        dR=diff(self.nodes, axis=0)
        dL=sqrt((dR**2).sum(1))
        dT=dL/(speed*self.speedfactor)
        t=concatenate(([0],cumsum(dT)))
        T=t[-1]

        x,y,z=transpose(self.nodes)
        n=x.size

        t2=linspace(0,T,round(T/timebase))


        tck=splrep(t,x,k=self.order)
        x2=splev(t2, tck)

        tck=splrep(t,y,k=self.order)
        y2=splev(t2, tck)

        tck=splrep(t,z,k=self.order)
        z2=splev(t2, tck)

        return transpose([x2, y2, z2])

    def translate(self, R):
        self.nodes=self.nodes+R
        return self

class Object:
    def __init__(self, strokes):
        self.strokes=strokes

    def rotate(angle, axis=[0,0,1]):
        newstrokes=[]
        for stroke in self.strokes:
            newstrokes+=[stroke.rotate(angle, axis)]
        self.strokes=newstrokes




def circle(radius, n=10):
    nodes=[]
    for theta in linspace(0, 2*pi, n+1):
        nodes+=[[radius*cos(theta), radius*sin(theta), 0]]
    return Stroke(nodes, order=2)

def polyline(nodes):
    return Stroke(nodes, order=1)

def rectangle(Lx, Ly, hspacing=.25):
    n=int(round(Ly/hspacing)+1)

    nodes=[]
    sign=1
    for y in linspace(-Ly/2., Ly/2., n):
        nodes+=[[-sign*Lx/2., y, 0], [sign*Lx/2., y, 0]]
        sign=-sign

    return Stroke(nodes, order=1)

def parallelepiped(Lx, Ly, Lz, hspacing=.25, vspacing=.25):
    strokes=[]
    nlayers=int(round(Lz/vspacing)+1)
    for z in linspace(-Lz/2., Lz/2., nlayers):
        layer=rectangle(Lx, Ly, hspacing=hspacing)
        layer.translate([0,0,z])
        strokes+=[layer]
    return Object(strokes)


class Writer(QtGui.QWidget):
    def __init__(self):
        super(Writer, self).__init__()

        self.v=DEFAULT_SPEED
        self.dt=DEFAULT_TIMEBASE

        self.glWidget = GLWidget()

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)

        self.setWindowTitle("TPP")

    def load(self, obj):
        self.target=obj
        self.updateTarget()

    def updateTarget(self):
        self.targetpaths=[]
        for stroke in self.target.strokes:
            self.targetpaths+=[stroke.pathCoords(self.v, self.dt)]

        self.glWidget.makeTargetList(self.targetpaths)


    def timebase(self, val=None):
        if val:
            self.dt=val
            self.updateTarget()
        else:
            return self.dt

    def speed(self, val=None):
        if val:
            self.v=val
            self.updateTarget()
        else:
            return self.v


    def write(self):
        mpv=30.
        ao_const(0,chan=0)
        ao_const(0,chan=1)
        ao_const(0,chan=2)
        time.sleep(0.5)
        x0=ai_single(chan=0)*mpv
        y0=ai_single(chan=1)*mpv
        z0=ai_single(chan=2)*mpv

        buildpaths=[]
        for path in self.targetpaths:
            #goto beginning of path
            x1,y1,z1=path[0]

            ao_const(x1/mpv,chan=0)
            ao_const(y1/mpv,chan=1)
            ao_const(z1/mpv,chan=2)
            time.sleep(0.5)


            vout=path/mpv
            #print vout.min(0), "  ", vout.max(0)
            vin=aio_waveform(self.dt, vout, chan=[0,1,2], rng=1)
            buildpath=vin*mpv-[x0,y0,z0]
            buildpaths+=[buildpath]
            self.glWidget.makeBuildList(buildpaths, self.targetpaths)

class GLWidget(QtOpenGL.QGLWidget):
    xRotationChanged = QtCore.pyqtSignal(int)
    yRotationChanged = QtCore.pyqtSignal(int)
    zRotationChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.path=[]
        self.zoom=1

        self.targetList = None
        self.buildList = None
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QtCore.QPoint()

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.updateGL()

    def initializeGL(self):
        #self.qglClearColor(self.trolltechPurple.dark())
        #self.glClearColor(0,0,0,0)
        #self.object = self.makeObject()
        GL.glShadeModel(GL.GL_FLAT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)

        #antialiasing
        GL.glEnable(GL.GL_BLEND);
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);
        GL.glEnable(GL.GL_LINE_SMOOTH);
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST);

        self.targetList = GL.glGenLists(1)
        self.buildList = GL.glGenLists(1)

    def paintGL(self):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        halfbox=10/self.zoom
        #GL.glOrtho(-halfbox, halfbox, halfbox, -halfbox, -50, 50)
        GLU.gluPerspective(20/self.zoom,1,1,50)
        GL.glMatrixMode(GL.GL_MODELVIEW)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(0.0, 0.0, -10.0)
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)

        if self.buildList:
            GL.glCallList(self.buildList)


        if self.targetList:
            GL.glCallList(self.targetList)


    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def wheelEvent(self, event):
        self.zoom*=2.**(event.delta()/1000.)
        self.updateGL()

    def makeTargetList(self, paths):
        GL.glNewList(self.targetList, GL.GL_COMPILE)
        GL.glColor4f(1,1,1, .5)

        for path in paths:

            GL.glBegin(GL.GL_LINE_STRIP)

            for point in path:
                GL.glVertex3d(point[0], point[1], point[2])

            GL.glEnd()

        GL.glEndList()

        self.updateGL()

    def makeBuildList(self, buildpaths, targetpaths):
        GL.glNewList(self.buildList, GL.GL_COMPILE)
        GL.glColor4f(0,1,0, 1)

        for path in buildpaths:

            GL.glBegin(GL.GL_LINE_STRIP)

            for point in path:
                GL.glVertex3d(point[0], point[1], point[2])

            GL.glEnd()

        GL.glEndList()

        self.updateGL()



    def clearBuildList(self):
        self.buildList=None
        self.updateGL()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

