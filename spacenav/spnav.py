from ctypes import *

EVENT_ANY=c_int(0)
EVENT_MOTION=c_int(1)
EVENT_BUTTON=c_int(2)

class spnav_event_motion(Structure):
	_fields_=[("type", c_int),
		    ("x",c_int),("y",c_int),("z",c_int),
		    ("rx",c_int),("ry",c_int),("rz",c_int),
		    ("period",c_uint),
		    ("data",c_void_p)]	

class spnav_event_button(Structure):
	_fields_=[("type",c_int),
		    ("press",c_int),
		    ("bnum",c_int)]

class spnav_event(Union):
	_fields_=[("type", c_int),
		    ("motion", spnav_event_motion),
		    ("button",spnav_event_button)]

libspnav=cdll.LoadLibrary("libspnav.so.0.1")

open=libspnav.spnav_open
open.restype=c_int

close=libspnav.spnav_close
close.restype=c_int

fd=libspnav.spnav_fd
fd.restype=c_int

sensitivity=libspnav.spnav_sensitivity
sensitivity.restype=c_int
sensitivity.argtypes=[c_double]

libspnav.spnav_poll_event.restype=c_int
libspnav.spnav_poll_event.argtypes=[c_void_p]

remove_events=libspnav.spnav_remove_events
remove_events.argtypes=[c_int]
remove_events.restypes=c_int

libspnav.spnav_wait_event.restype=c_int
libspnav.spnav_wait_event.argtype=[c_void_p]

#blocks waiting for space-nav events. returns 0 if an error occurs
sev=spnav_event(0)

def poll_event():
  res=libspnav.spnav_poll_event(pointer(sev))
  return int(res)


def wait_event():
  libspnav.spnav_wait_event(pointer(sev))
  #return sev



