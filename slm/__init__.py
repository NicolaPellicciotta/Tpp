import siteconf
from dvislm import *
from bnsslm import *

if siteconf.slm=="boulder":
  Modulator=BNSmodulator
elif siteconf.slm in ["hamamatsu","hamamatsu-NIR", "holoeye"]:
  Modulator=DVImodulator
