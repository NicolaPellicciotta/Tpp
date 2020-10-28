from tweezers import *

def axicon(L,fpos=[0.,0.,0.],shift=[-30,30],objMag=60.,objNA=1.4,pixelsize=20.):
    H=slm.height
    W=slm.width

    flength=1000*200./objMag
    NA=objNA
    Robj=flength*NA/pixelsize        

    xvec=linspace(-W/2.+0.5,W/2.-0.5,W)+shift[0]
    yvec=linspace(-H/2.+0.5,H/2.-0.5,H)+shift[1]
    X,Y=meshgrid(xvec,yvec)    

    axholo=sqrt(X**2+Y**2)/Robj*L
    axholo=mod(axholo,1)*2*pi-pi


    h=holo(trap(fpos[0],fpos[1],fpos[2]))
    axholo=mod(h+axholo,2*pi)

    imshow(axholo,cmap=cm.gray)
    circ=plt.Circle((W/2,H/2),Robj,facecolor='none',edgecolor='r')
    gca().add_artist(circ)
    fig=gcf()
    fig.canvas.draw()
    show()    


    return axholo

def apertureHolo(Asize=66.,spotD=10.,objMag=60.,objNA=1.4,pixelsize=20.):
    '''
    Makes a hologram that is divided into circular subapertures.
    The subapertures are arranged in a polar grid to fit the 
    objective's back aperture. Each circular supaperture holds a 
    unique grating projecting its own low-NA focus in the focal plane.
    The position of each low-NA focus is reflecting the position of its
    "mother" subaperture in the hologram (thus on the SLM).

    -Asize is the diameter of the circles subapertures in pixels
    -spotD is the distance between the first orders
    -objMag: magnification of the objective
    -objNA:  numerical aperture of the objective
    -pixelsize: pixel size of the SLM on the objectives back focal plane,
                its value is the original pixel size of the SLM multiplied 
                by the 4f system's beam-expansion ratio

    objMag, objNA, pixelsize are used to calculate the radius of the 
    objective's back focal plane in units of SLM pixels
    The background between and around the subapertures 
    is a high grating to send light away (instead of letting it go to the 0th order)
    '''

    H=slm.height
    W=slm.width
    flength=1000*200./objMag
    NA=objNA

    Robj=flength*NA/pixelsize

    temp=linspace(-Asize/2.+0.5,Asize/2.-0.5,Asize)
    X,Y=meshgrid(temp,temp)
    cmask=sqrt(X**2+Y**2)<=Asize/2
    idx=find(cmask)
    row=idx%Asize
    col=idx/Asize
    ox=W/2
    oy=H/2

    #the background is a grating sending the light far from the 0th order
    apertureholo=holo(trap(100,100)) 

    spotD=10.0 #distance of first orders
    xshift=0.
    yshift=0.
    #holographic coordinates:
    xcoors=[]
    ycoors=[]
    #Aperture center coordinates:
    axSLM=[]
    aySLM=[]

    radialshift=0
    angleshift=0

    for r in arange(0+radialshift*3/2.*Asize,Robj-Asize/2,Asize):
        #if (r>=(3.*Asize)) and (r<(4.*Asize)):
         #   continue
        aN=floor(r*2*pi/Asize) #number of micro apertures with circle r
        if aN==0:
            ares=360.
            aN=1
        else: ares=360./aN
        avec=arange(aN)*ares+angleshift*ares/2
        x=r*cos(avec/180.*pi)+ox-Asize/2
        y=r*sin(avec/180.*pi)+oy-Asize/2
        for i in range(len(x)):
            xcoors+=[r/Asize*cos(avec[i]/180.*pi)*spotD+xshift]
            ycoors+=[ r/Asize*sin(avec[i]/180.*pi)*spotD+yshift]
            h=holo(trap(xcoors[-1],ycoors[-1]))
            
            for j in arange(len(row)):
                ri=int(round(row[j]+y[i]))
                ci=int(round(col[j]+x[i]))
                apertureholo[ri,ci]=h[ri,ci]


        axSLM+=list(x+Asize/2)
        aySLM+=list(y+Asize/2)
        
    #traps=[]
    #for i in range(len(xcoors)):
    #    traps+=[trap(xcoors[i],ycoors[i])]
    #    
    #refholo=holo(traps,n=30)

    imshow(apertureholo,cmap=cm.gray)
    circ=plt.Circle((W/2,H/2),Robj,facecolor='none',edgecolor='r')
    gca().add_artist(circ)
    fig=gcf()
    fig.canvas.draw()
    show()
    return apertureholo


def singleapertureHolo(Asize=66.,Apos=[0.5,0],fpos=[10.,10.,0.],bckpos=[0.,0.],axif=0,objMag=60.,objNA=1.4,pixelsize=20.):
    '''
    calculates a grating for a focus at (fpos=[fx,fy,fz], um) 
    the grating is masked with a circular subaperture with diameter Asize (pixels)
    the subaperture's center position is defined in polar coordinates by Apos=[r,phi]
    within the unit circle of the objectives back focal plane.
    outside the subaperture the hologram is a grating sending light to bckpos=[fx,fy], um
    '''
    H=slm.height
    W=slm.width
    flength=1000*200./objMag
    NA=objNA

    Robj=flength*NA/pixelsize

    temp=linspace(-Asize/2.+0.5,Asize/2.-0.5,Asize)
    X,Y=meshgrid(temp,temp)
    cmask=sqrt(X**2+Y**2)<=Asize/2

    idx=find(cmask)
    row=idx%Asize
    col=idx/Asize
    ox=W/2
    oy=H/2

    #the background is a grating sending the light far from the 0th order
    apertureholo=holo(trap(bckpos[0],bckpos[1])) 
    
    R=Apos[0]
    phi=Apos[1]
    x=R*cos(phi)*Robj+ox-Asize/2
    y=R*sin(phi)*Robj+oy-Asize/2

    #insert the subaperture:
    h=holo(trap(fpos[0],fpos[1],fpos[2]))
    axih=axicon(axif)
    h=mod(h+axih,2*pi)
    for j in arange(len(row)):
        ri=int(round(row[j]+y))
        ci=int(round(col[j]+x))
        apertureholo[ri,ci]=h[ri,ci]

    imshow(apertureholo,cmap=cm.gray)
    circ=plt.Circle((W/2,H/2),Robj,facecolor='none',edgecolor='r')
    gca().add_artist(circ)
    fig=gcf()
    fig.canvas.draw()
    show()
    return apertureholo











