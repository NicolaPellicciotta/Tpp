import serial
import time
import string
import world

from numpy import  array

class prior:
	"""class prior()
	
	Description:
		opens the serial bus and prints info about settings
		enables communication with the PRIOR motor
	
	Methods:
		info\t- prints out stage status info
		pos\t- returns stage position
		mv\t- move absolute
		mvr\t- move relative
		ss\t- set stage speed
		fs\t- set focus speed
		stop\t- set speed to 0
		send\t- sends a string over the serial channel
		flushIO\t- flushes I/O channels	
"""
	def __init__(self):
		self._ser= serial.Serial(0)
		self._ser.timeout=1
		self.verbose=False
		scorrection=1.0
		self._sreso=.1/scorrection #stage horizontal motion units in microns
		self._freso=.1 #z motion units in microns
		if world.stage is not None:
			raise AssertionError, "There's an open stage in the world"
		world.stage=self
		#self.info()

	def __repr__(slef):
		return "PRIOR PROSCAN"
 
	def flushIO(self):
		self._ser.flushInput()
		self._ser.flushOutput()
		

	def info(self):
		self.flushIO()
		print "\nXY info:"
		self._ser.write("STAGE\r")
		answer=""
		while answer != "END\r":
			#answer=self._ser.readline(eol='\r')
			answer=self._ser.readline()
			print answer
			
		print "\nZ info:"			
		self._ser.write("FOCUS\r")
		answer=""
		while answer != "END\r":
			#answer=self._ser.readline(eol='\r')
			answer=self._ser.readline()
			print answer

	def pos(self):	
		"""returns the array of stage position coordinates"""
		x=string.atoi(self.send("PX"))*self._sreso
		y=string.atoi(self.send("PY"))*self._sreso
		z=string.atoi(self.send("PZ"))*self._freso

		return array([x,y,z])
	
  def readline(self):
        ans=''
        c=self._ser.read(1)
        while c != '\r':
            ans+=c
            c=self._ser.read(1)
        return ans


	def send(self,message):
		self.flushIO()

		self._ser.write(message+"\r")
		#ans=self._ser.readline(eol='\r')
		ans=self.readline()

		if self.verbose:
			print "sent: "+message
			print "received: "+ans
		return ans

	def mv(self, x,y,z=0):
		"""move to absolute position x,y,z"""
		if x!=0 or y!=0:
			cmd="G %f, %f" % (x/self._sreso,y/self._sreso)
			self.send(cmd)

		if z!=0:
			cmd="PZ %f" % (z/self._freso)
			self.send(cmd)


	def mvr(self, x,y,z=0):

		if x!=0 or y!=0:
			cmd="GR %f, %f" % (x/self._sreso,y/self._sreso)
			self.send(cmd)

		if z!=0:
			cmd="U %d" % (z/self._freso)
			self.send(cmd)
			
	def ss(self,vx,vy):
		cmd="VS %f,%f" % (vx,vy)
		self.send(cmd)
	
	
	def fs(self,vz):
		cmd="OF %d" % (vz)
		self.send(cmd)
	
	def stop(self):
		self.ss(0,0)
		self.fs(0)



class tango:
    """class tango()
    
    Description:
        opens the serial bus and prints info about settings
        enables communication with the PRIOR motor
    
    Methods:
        info\t- prints out stage status info
        pos\t- returns stage position
        mv\t- move absolute
        mvr\t- move relative
        ss\t- set stage speed
        fs\t- set focus speed
        stop\t- set speed to 0
        send\t- sends a string over the serial channel
        flushIO\t- flushes I/O channels    
"""
    def __init__(self):
        self._ser= serial.Serial(0, baudrate=57600, stopbits=2)
        self._ser.timeout=1
        self.verbose=False
        self.send('!dim 1 1',False)
    #if world.stage is not None:
    #    raise AssertionError, "There's an open stage in the world"
    #world.stage=self
        self.info()

    def __repr__(slef):
        return "TANGO"
 
    def readline(self):
        ans=''
        c=self._ser.read(1)
        while c != '\r':
            ans+=c
            c=self._ser.read(1)
        return ans

    def send(self,message,resp=True):
        self.flushIO()

        self._ser.write(message+"\r")
        #ans=self._ser.readline(eol='\r')
        ans=""
        if resp: 
            ans=self.readline()

        if self.verbose:
            print "sent: "+message
            print "received: "+ans
        return ans


    def flushIO(self):
        self._ser.flushInput()
        self._ser.flushOutput()
       

    def info(self):
        self.flushIO()
        print "\nXY info:"
        answer=self.send("?pos")
        print answer
            
    def pos(self):    
        """returns the array of stage position coordinates"""
        x=string.atof(self.send("?pos x"))
        y=string.atof(self.send("?pos y"))
        return array([x,y])


    def mv(self, x,y,z=0):
        """move to absolute position x,y,z"""
        if x!=0 or y!=0:
            cmd="!moa %f %f" % (x,y)
            self.send(cmd,False)

    def mvr(self, x,y):
        if x!=0 or y!=0:
            cmd="!mor %f %f" % (x,y)
            self.send(cmd,False)
            
    #def ss(self,vx,vy):
    #    cmd="!speed %f %f" % (vx,vy)
    #    self.send(cmd,False)
    
    #def stop(self):
    #    self.ss(0,0)

