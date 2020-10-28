import os
from numpy import *
from matplotlib.mlab import *
import matplotlib.pyplot as plt

def mkDirIfNotExists(directory_path):
    """
    make a directory if it does not already exist
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print 'the directory %s has been created' %directory_path

def getAttributeListfromClassList(class_list, attr_name):
    '''
    devo prenderlo solo il valore e' definito altrimenti ci mette NaN
    '''
    attribute_list=[]
    for obj in class_list:
        if hasattr(obj, attr_name):
            attribute_list+=[getattr(obj, attr_name)]
        else:
            attribute_list+=[nan]
    return attribute_list

def mode(array):
    n,be=histogram(array)
    idx=find(n==n.max())[0]
    return 0.5*(be[1:]+be[:-1])[idx]

def mySleep(dt):
    os.system('sleep '+str(dt))

def distMatrix2D(a, b=None):
    '''
    this functions takes as input to array of point in 2D and compute the distance
    of points in a with points in b. distance Matrix in 2D space
    this takes advantage of complex numbers
    '''
    a=array([[complex(_[0], _[1]) for _ in a]])
    if b==None:
        b=a
    else:
        b=array([[complex(_[0], _[1]) for _ in b]])
    dMatrix = abs(a.T-b)

    return dMatrix

def array2couples(x1, x2):
    x1=array([x1]*len(x2))
    x2=array([x1]*len(x1)).T
    return x1,x2
    
def fitLimits(y):
    axes=plt.gca()
    ymin, ymax=axes.get_ylim()
    ymin=min(ymin, y.min())
    ymax=max(ymax, 1.1*y.max())
    #print ymin, ymax
    axes.set_ylim(ymin, ymax)

def apply2allfigures(func):
    figures=[manager.canvas.figure
         for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
    for i, fig in enumerate(figures):
        func(fig)

def getpoint_fromfig():
    fig=gcf()
    while True:
        cp=fig.ginput(0)
        if len(cp)>0:
            break

    return cp[-1]


def be2bx(be):
    bx=(be[1:]+be[:-1])/2.
    return bx

def funhist(x,y, bins=256, rng=None):
    hn,be=histogram(x, bins=bins, range=rng)
    hx, be=histogram(x, weights=x, bins=bins, range=rng)
    hy,be=histogram(x, weights=y, bins=bins, range=rng)
    hy2, be=histogram(x, weights=y**2, bins=bins, range=rng)
    hx=hx[hn>0]/hn[hn>0]
    hy=hy[hn>0]/hn[hn>0]
    hy2=hy2[hn>0]/hn[hn>0]
    return hn, hx, hy, hy2-hy**2
