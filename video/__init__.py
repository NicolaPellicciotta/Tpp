from PyQt4 import QtGui
import subprocess as sp
import tempfile, shutil

class Video:
  def __init__(self, w, h, filename=None, mode='MONO8', fps=24, compression=10):
    if mode=='RGB':
      nbits=w*h*24
      pix_fmt='rgb24'
    elif mode=='MONO8':
      nbits=w*h*8
      pix_fmt='gray'

    if filename is None:
      self.filename=tempfile.mktemp(prefix="camvideo-")

    bitrate=nbits*fps/1.e3
    bstr="%.0dk" % (bitrate/compression)
    self.pipe=sp.Popen(['ffmpeg',
      '-y',       #overwrite output file
      '-s', '%dx%d' % (w, h),
      '-f', 'rawvideo',
      '-vcodec', 'rawvideo',
      '-pix_fmt', pix_fmt,
      '-r', '%d' % fps,
      '-i', '-',  # stdin
      '-an',      # no audio
      '-f', 'mp4',
      '-vcodec', 'mpeg4',
      '-pix_fmt', 'yuv420p', #seems to be a very common one
      '-b', bstr,
      self.filename],
      stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

  def append(self, data):
    data.tofile(self.pipe.stdin)

  def close(self):
    self.pipe.stdin.close()
    self.pipe.wait()
    self.d=QtGui.QFileDialog()
    self.d.fileSelected.connect(self.rename)
    self.d.show()

  def rename(self, filename):
    shutil.move(self.filename, filename)

  def log(self):
    for line in self.pipe.stderr.readlines():
      print line

#class recorder:
#  def __init__(self, filename):
#    self.filename=filename
    #self.button=QtGui.QButton("Stop")
    #self.button.clicked.connect(self.stop)
    #self.button.show()

#  def capture(self, roi):

#  def append(self, data):

#  def stop(self):
#    vid.close()
    #self.button.close()


#  self.video=Video('test.mp4'


def frames2vid(filename, frames, fps=24, compression=10):
  vid=Video(filename, frames[0], fps=fps, compression=compression)
  for f in frames:
    vid.append(f)
  vid.close()
