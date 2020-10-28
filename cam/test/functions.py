from holocam.frames import *
import time

def prova(stack, n):
  #stack=framestack(n, filename="run")
  ccd.stream()
  t=[]
  for i in range(n):
    f=ccd.capture()
    t+=[f.time]
    #data=zeros((1024, 1024))
    stack.append(f.data)
  ccd.stop()
  #stack.close()
  return array(t)-t[0]

def prova2(n):
  #stack=framestack(n, filename="run")
  ccd.stream()
  t=[]
  for i in range(n):
    f=ccd.capture()
    t+=[f.time]
    #data=zeros((1024, 1024))
    #stack.append(f.data)
    np.save("frame-%d.npy" % i, f.data)
  ccd.stop()
  return array(t)-t[0]
  #stack.close()


# prova(100)
