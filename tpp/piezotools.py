from comedi import* 
import cPickle as pickle
import utils
import scipy
from scipy.optimize import leastsq
from matplotlib.pyplot import *
from mayavi import mlab as mayalab
from numpy import *

class PiezoDynamics:
    pass

def sqwave(amp,period,timestep,duration):
    Npoints=floor(duration/timestep)
    pointsPerPeriod=period/timestep
    wave=zeros(Npoints)
    mask=mod(arange(Npoints),pointsPerPeriod)>(pointsPerPeriod/2)
    wave[mask]=amp
    return wave

def triwave(amp,period,timestep,duration):
    mask=sqwave(1,period,timestep,duration)>0
    wave=mod(arange(len(mask)),period/timestep)
    wave[mask]=(period/timestep)-wave[mask]
    wave=wave/wave.max()*amp
    return wave
    
def pulsewave(amp,t0,timestep,duration):
    Npoints=floor(duration/timestep)
    wave=zeros(Npoints)
    wave[round(t0/timestep)]=amp
    return wave

def measureIPR(amp,t0,timestep,duration,Navg=20,ch=0):      

    pulse=pulsewave(amp,t0,timestep,duration)
    iprs=[]

    for i in range(Navg):    
        ipr=aio_waveform(timestep,pulse,chan=ch,rng_in=0,rng_out=0)
        time.sleep(1)
        iprs+=[ipr]
    iprs=array(iprs).squeeze()
    ipr=iprs.mean(0)
    starti=round(t0/timestep)
    ipr-=mean(ipr[:starti*0.75])
    figure()
    t=arange(len(pulse))*timestep
    #plot(t,pulse,'b.-',markerfacecolor='g')
    plot(t,ipr,'r.-',markerfacecolor='k')

    ipr=ipr[starti:]/amp
    t=arange(len(ipr))*timestep
    return ipr,t

def measurePiezoDyn(amp=0.333,t0=0.1,timestep=0.001,duration=1.5,Navg=20):

    piDyn=PiezoDynamics()
    iprs=[]
    tfs=[]
    tf_fits=[]
    for i in range(3):
        ipr,t=measureIPR(amp,t0,timestep,duration,Navg=Navg,ch=i)
        tf,freq=getTF(ipr,timestep)
        tf_fit=fitTF(freq,tf,nlor=4,fmax=(85. if i<2 else 150))
        iprs+=[ipr]
        tfs+=[tf]
        tf_fits+=[tf_fit]

    piDyn.Iprs=iprs
    piDyn.Ipr_t=t  
    piDyn.Tfs=tfs
    piDyn.Tf_fits=tf_fits
    piDyn.TF_freq=freq    
    piDyn.Ipr_dt=timestep

    return piDyn

def plotTF(freq,tf):
    figure()
    plot(freq,abs(tf),'.-',markerfacecolor='g',markeredgecolor='g')
    xlim(xmin=freq[0])

def getTF(ipr,dt):
    fipr=fft.fft(ipr,n=len(ipr))  
    freq=fft.fftfreq(len(ipr),dt)
    #plotTF(freq,fipr)
    return fipr,freq

def lowPassFilter(freq,y,cutoff,o=1):
    lpf=1.0/(1+(freq/cutoff)**(2*o))
    return y*sqrt(lpf)

def lorentzianComplex(w,x):
    return w/(1j*x+w)
        
def sumLorentzians(p,x):
    y=lorentzianComplex(1/p[0],x)
    for i in range(1,len(p)):
        y*=lorentzianComplex(1/p[i],x)
    return y

def lorfitcostFun(p,x,y):
    yt=sumLorentzians(p,x)
    return append(real(y-yt),imag(y-yt))
            
def fitTF(freq,tf,fmax=85.,nlor=2):
    cond=abs(freq)<fmax
    p0=0.2**(arange(nlor)+1)
    p=leastsq(lorfitcostFun,p0,args=(freq[cond],tf[cond]))[0]
    tf_fitted=sumLorentzians(p,freq)
    #plot the amplitude TF:
    figure()
    plot(freq,abs(tf))
    plot(freq,abs(tf_fitted))
    xlim((-fmax,fmax))
    figure()
    plot(freq,angle(tf))
    plot(freq,angle(tf_fitted))
    xlim((-fmax,fmax))
    return p

def precompensate(wave,dt,tf_fit,lpfreq,lpo):

    wave=wave.copy()
    
    #pad wave to eliminate artefacts of the prefilter:
    ps_front=int(round(1.5/dt))
    ns=int(len(wave)+2*ps_front)
    ps_back=int((1<<(ns-1).bit_length())-ns+ps_front)

    wave=wave.copy()
    wave=concatenate([zeros(ps_front)+wave[0],wave,zeros(ps_back)+wave[-1]])
    
    #pad wave to the a power of 2 size:            
    fwave=fft.fft(wave)
    freq=fft.fftfreq(len(wave),dt)

    #create the fitted transfer function:    
    tf2=sumLorentzians(tf_fit,freq)

    #pre-compensated and filtered wave:
    fwave_c=fwave/tf2
    fwave_c=lowPassFilter(freq,fwave_c,lpfreq,o=lpo)
    wave_c=real(fft.ifft(fwave_c))

    wave_c=wave_c[ps_front:-ps_back]
    return wave_c

def testscan3D(teststr,piDyn,lpfreqs,lpos):

    #get the current position averaged:
    vpos0=ai_waveform(0.0001,1000,chan=[0,1,2],rng=0).mean(0)
    vpos0[2]-=5./30.    

    #array for the positions read during the scan:
    posread=array([[],[],[]]).transpose()
    #array for the deviations from the structure coordinates:
    scndev=array([])    

    for si in teststr.Strokes:
        
        #get the interpolated coordinates of the current stroke:
        icoors,dt=si.icoors() 
        vout=icoors/30   
        vout[:,2]=-vout[:,2]   #PIEZO Z-axis is upside down
        vout_c=zeros_like(vout)

        #send the piezo to the start position of the Stroke
        ao_const(vout[0,0],chan=0)
        ao_const(vout[0,1],chan=1)
        #ao_const(vout[0,2],chan=2)  
      
        #precompensate for the piezo dynamics:
        for ci in range(3):
            vout_c[:,ci]=precompensate(vout[:,ci],dt,piDyn.Tf_fits[ci],lpfreqs[ci],lpos[ci])

        #mlab.plot3d(vout_c[:,0]*30,vout_c[:,1]*30,vout_c[:,2]*30,color=(1,0,0),tube_radius=None,line_width=1.)

        time.sleep(0.25)

        #(open shutter):               
        ao_const(vout[0,2],chan=2)

        #do the scan:
        vread=aio_waveform(si.dt,vout_c,chan=[0,1,2],rng=0)
        
        #(close shutter):               
        ao_const(5/30.0,chan=2)
        time.sleep(0.25)

        pr=(vread-vpos0)*30.
        pr[:,2]*=-1#PIEZO Z-axis is upside down   
        scndev=append(scndev,sqrt(sum((pr-icoors)**2,axis=1)))
        posread=append(posread,pr,axis=0)

    #reset the driving voltage to zero
    ao_const(0.0,chan=0)
    ao_const(0.0,chan=1)
    ao_const(5/30.0,chan=2)

    teststr.plot()
    mayalab.plot3d(posread[:,0],posread[:,1],posread[:,2],scndev*1000,colormap="blue-red",
                tube_radius=None,line_width=1.5)
        #scale_factor=0.05,colormap="blue-red",scale_mode='none')        
    mayalab.colorbar(nb_labels=5,orientation='vertical') 

    print('max dev:' +str(scndev.max()*1000) + 'nm')    
    print('std-dev:' +str(std(scndev)*1000) + 'nm')   

    return posread
        
def simscan(wave,dt,ipr,ipr_dt,tf_fit,lpfreq,lpo):
    
    #pad wave:
    padsize=round(1.5/dt)
    wave=wave.copy()
    wave=concatenate([zeros(padsize)+wave[0],wave,zeros(padsize)+wave[-1]])       

    #interpolate the measured impulse response
    #with the dt timestep of the wave:
    ipr=ipr.copy()
    ipr/=sum(ipr)
    ipr_t=arange(len(ipr))*ipr_dt
    ipr2_t=arange(0.,len(ipr)*ipr_dt,dt)
    ipr2=scipy.interp(ipr2_t,ipr_t,ipr)*dt/ipr_dt
    #get the transfer function:
    tf=fft.fft(ipr2,n=len(wave))  
    freq=fftfreq(len(tf),dt)

    fwave=fft.fft(wave)
    #create the fitted transfer function:    
    tf2=sumLorentzians(tf_fit,freq)
    #pre-compensated and filtered wave:
    fwave_c=fwave/tf2
    fwave_c=lowPassFilter(freq,fwave_c,lpfreq,o=lpo)
    wave_c=real(fft.ifft(fwave_c))
    #simulate the piezo:
    yc=real(fft.ifft(fwave_c*tf))
    ynoc=real(fft.ifft(fwave*tf))
    figure(figsize=(10,10))
    plot(wave[padsize:-padsize])
    plot(wave_c[padsize:-padsize],'b--')
    plot(yc[padsize:-padsize])
    plot(ynoc[padsize:-padsize])
    #xlim((0,10000))
    #ylim((-0.01,wave_c[10000]*1.2))
    title('lowpass freq: ' + str(lpfreq) + '  lowpass filter order: ' +str(lpo))    

def saveMeas(pd):
    fname='piezoDynamics'
    with open(fname, 'w') as f:
        pickle.dump([pd],f)

def loadMeas(fname):

    with open(fname, 'r') as f:
        pd=pickle.load(f)[0]
    return pd


    



















