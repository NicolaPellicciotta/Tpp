#Global variables for hardware configuration EDIT IF SETUP CHANGES
import numpy

hostname="tpp"
#slm="hamamatsu-NIR"
slm="hamamatsu"
#slm="holoeye"
#slm="boulder"

#camera="orca"
#camera="basler"
camera="avt_gige"
#camera="mikrotron"



#CALIBRATION

#FILE: ./calibration/18-07-14_ThorlabsR1L3S2P_Mikrotron_100xlambda
mpp=0.091980546603519286

#FILE: ./calibration/matrixRGB_07-11-13_Baler2Prizmatix.npy')
basler_rgb_matrix_cal=[[ 1.01289143, -0.13710277,  0.06231835],[-0.10100076,  1.18158022, -0.65640251],[-0.05964939, -0.29353457,  1.16423904]]
#SLM aberration
aberration=numpy.load("/home/roberto/Documents/Dev/Python/slm/aberrations/abfunc_220618_60x.npy")
#aberration=numpy.load("/home/roberto/Documents/Dev/Python/slm/aberrations/abfunc_051119_60x.npy")
LUT=numpy.load("/home/roberto/Documents/Dev/Python/slm/LUT_785.npy")
slm_shift=[17, -37]#None 051119
#FILE: None
trap_cal_matrix=[[1,0,0],[0,1,0],[0,0,1]]





