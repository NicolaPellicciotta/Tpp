from PyQt4 import QtCore, QtGui

class interactive_loop:
    '''
    Iterates a list (iterlist) and a calls function (fun) without blocking Qt main loop.
    Use it in a loop where a camera view is shown after each iteration.

    Equivalent of to:
    rets=[]
    for val in iterlist:
        rets+=[fun(val,args)]
        sleep(dt)

    Parameters:
        fun -- function
        iterlist -- arguments of the function
        dt -- qt timer delay
        args -- tuple of additional optional arguments of fun

    Example (print message N times):

    def pippo(i,message):
        print message
        return 0

    iloop=interactive_loop(pippo,arange(N),dt=0.5,args="a message")
    iloop.start() 
    rets=iloop.stop() 
    '''
    def __init__(self, fun, iterlist, dt=0, args=None):
        self._fun=fun       
        self._iterlist=iterlist
        self._niter=len(iterlist)
        self._i=0
        self._dt=dt*1000.
        self._args=args
        self._timer=QtCore.QTimer()
        self._timer.timeout.connect(self._action)
        self._timer.setSingleShot(True)
        self._RUNNING=False
    
    def start(self):
        self._retlist=[]
        self._timer.start(0)
        self._RUNNING=True

    def stop(self):
        self._RUNNING=False
        return self._retlist

    def _action(self):
        if self._RUNNING:
            val=self._iterlist[self._i]
            if self._args: self._retlist+=[self._fun(val,self._args)]
            else: self._retlist+=[self._fun(val)]
            self._i+=1
            if self._i<self._niter:
                self._timer.start(self._dt)
            else:
                self._RUNNING=False
                self._i=0

