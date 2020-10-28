from pylab import *

def calc_dIdx(t, i, dt_max, dt_min=0.1, max_dt_idx=50):
    #max_dt_idx=int(fps*dt)+1
    if 0.8*dt_max<dt_min:
        dt_min=0.8*dt_max
    try:
        for di in arange(max_dt_idx, 0, -1, dtype=int):       
            difft=t[i+di]-t[i]
            if (difft<dt_max)*(difft>dt_min):
                return di
    except IndexError:
        return nan
    #if dt_min< !!! dt_min must be at least the minimum difference of frames
    return nan
        
def diff_idxs(t, dt, fps):
    '''
    this functions return 2 list of indices thus that t[i2]-t[i1]~=dt;
    if some time is skipped, the time difference between 2 frames is bounded in the interval
    0.1<t[i2]-t[i1]<dt
    '''
    max_dt_idx=int(fps*dt)+1    
    dIdxs=amap(lambda i:calc_dIdx(t, i, dt, max_dt_idx=max_dt_idx), arange(len(t)))
    i1=arange(len(t))[~isnan(dIdxs)]
    i2=i1+dIdxs[~isnan(dIdxs)].astype(int)
    return i1, i2
