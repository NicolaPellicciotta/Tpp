import pickle
import socket
from numpy import *
import siteconf
import world

def rad2byte(holo):
	  """Returns a 0..255 hologram from a radians phase holo"""
	  lpr=256./2./pi
	  return mod(lpr*holo, 256).round().astype(uint8)

class BNSmodulator():
    def __init__(self):
        if world.slm:
            raise Exception("There's an open SLM in the world")    
        if siteconf.slm == "boulder":
            self.width=256
            self.height=256
            self.mpp=24.
            self.lam=0.532
            self.aberration=siteconf.aberration
            self.lut=None

        self.displayedholo=zeros((self.height,self.width),dtype=uint8)
        self._size=len(pickle.dumps(self.displayedholo,2))
        self.createConnection()
    
    def createConnection(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_address = ('192.168.2.3', 10000)
        print 'connecting to %s port %s' % self._server_address
        self._sock.connect(self._server_address)
        print 'ok'

    def closeConnection(self):
        self._sock.close()
        del self._sock

    def _send(self, msg):
        totalsent = 0
        while totalsent < self._size:
            sent = self._sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def show(self,holo):
        assert(shape(holo)==(self.height,self.width))
        #prepare hologram
        if holo.dtype!=uint8:
            self.displayedholo=rad2byte(holo)
        else:
            self.displayedholo=holo
        if self.aberration!=None:
            self.displayedholo+=self.aberration
        #send hologram
        rawdata=pickle.dumps(self.displayedholo,2)
        self._send(rawdata)
        #check for errors
        #if int(self._sock.recv(1)):
        #    raise Exception('Error: check exception string on server')
        
    def __del__(self):
        self.closeConnection()
        del self.aberration,self.displayedholo



