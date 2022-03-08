# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 14:19:09 2022

@author: Scott Greenwood
"""

import numpy as np

def isBinary(x):
    try:
        n = len(x)
    except:
        n = 0
        
    if n == 0:
        if not (x == 1 or x == 0):
            raise ValueError("x has non-binary (1/0) values")
    else:
        for i in range(n):
            if not (x[i] == 1 or x[i] == 0):
                raise ValueError("x has non-binary (1/0) values")
        
def xor(u1,u2):
    n = len(u1)
    
    isBinary(u1)
    isBinary(u2)

    y = np.zeros(n)
    for i in range(n):
        if not u1[i] == u2[i]:
            y[i] = 1
    return y  
  
def max_len_seq(seed=[1,0,1], generator = [1,1,0,1], bias = 0):
    '''
    Predefined generator values that give the max length sequence are taken from: https://en.wikipedia.org/wiki/Linear-feedback_shift_register#Some_polynomials_for_maximal_LFSRs
    Create a PRBS or maximum lenqth sequence binary array. 
    
    !! Caution: Incorrect generator will cause issues. See scipy.signal.max_len_seq for proper generators based on sequence.
    '''
    nBit = len(seed)
    nVal = int(2**(nBit)-1)
    seed_int = np.concatenate(([0],seed))
        
    if not np.sum(np.abs(seed)) > 0:
        raise ValueError("seed must contain at least one 1")
     
    y_int = np.zeros(nVal)
    for i in range(nVal):
        y_int[i] = seed_int[-1]
        for j in range(nBit):
            seed_int[j] = seed_int[j + 1]
        seed_int[nBit] = 0
        if seed_int[0] == 1:
            seed_int = xor(seed_int,generator)
        
    y = np.zeros(nVal)
    for i in range(nVal):
      y[i] = y_int[i] + bias
    return y

def max_len_seq_ternary(seed=[0,1,2], generator = [1,2,2], bias = 0):
    nBit = len(seed)
    nVal = int(3**(nBit)-1)
    seed_int = np.array(seed)
    
    if not np.sum(np.abs(seed)) > 0:
        raise ValueError("seed must contain at least one 1")
        
    y_int = np.zeros(nVal)
    y = np.zeros(nVal)
    for i in range(nVal):
        y_int[i] = np.mod(sum(generator*seed_int), 3)
        for j in range(nBit-1):
            seed_int[nBit-j-1] = seed_int[nBit-j-2]
        seed_int[0] = int(-1 if y_int[i] == 2 else y_int[i])
        y[i] = seed_int[0] + bias
    return y

def noise(mls, freqHz=1,amplitude=1,offset=0,startTime=0,nPeriods=None,stopTime=None,collapse=True):
    
    if nPeriods != None:
        nSamples = len(mls)*nPeriods
    elif stopTime != None:
        nSamples = int((stopTime - startTime)*freqHz)
    else:
        raise ValueError('Unknown option. nPeriods or stop_time must not be None')
     
    time = np.zeros(nSamples)
    y = np.zeros(len(time))
    j = 0
    dt = 1/freqHz
    for i in range(len(time)):
        time[i] = dt*i
        dy = amplitude*mls[j]
        y[i] = offset + dy
        if j+1 > len(mls)-1:
            j = 0
        else:
            j += 1
    
    if collapse:
        ynew = []
        timenew = []
        ynew.append(y[0])
        timenew.append(time[0])
        for i in range(len(y)-1):
            if y[i+1] != y[i]:
                ynew.append(y[i+1])
                timenew.append(time[i+1])
        y = np.array(ynew)
        time = np.array(timenew)
        
    if startTime != 0:
        time = np.concatenate(([0],time+startTime))
        y = np.concatenate(([offset],y))
    return time, y

def prbs(bias=0, nBits=3, seed=None, freqHz=1, amplitude=1, offset=0, startTime=0, nPeriods=None, stopTime=None, collapse=True):
    if seed == None:
        seed=np.concatenate(([1],np.zeros(nBits-2,dtype='int'),[1]))
    genOptions = {2:[1,1,1],
                  3:[1,1,0,1],
                  4:[1,1,0,0,1],
                  5:[1,0,1,0,0,1],
                  6:[1,1,0,0,0,0,1],
                  7:[1,1,0,0,0,0,0,1],
                  8:[1,0,1,1,1,0,0,0,1],
                  9:[1,0,0,0,1,0,0,0,0,1],
                  10:[1,0,0,1,0,0,0,0,0,0,1],
                  11:[1,0,1,0,0,0,0,0,0,0,0,1],
                  12:[1,1,1,0,0,0,0,0,1,0,0,0,1],
                  13:[1,1,1,0,0,1,0,0,0,0,0,0,0,1],
                  14:[1,1,1,0,0,0,0,0,0,0,0,0,1,0,1],
                  15:[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1]}
    if not nBits in genOptions:
        generator = np.zeros(nBits+1,dtype='int')
    else:
        generator = genOptions[nBits]
    mls = max_len_seq(seed, generator, bias)
    
    time, y = noise(mls=mls, freqHz=freqHz,amplitude=amplitude,offset=offset,startTime=startTime,nPeriods=nPeriods,stopTime=stopTime,collapse=collapse)
    return time, y


def prts(bias=0, nBits=3, seed=None, freqHz=1, amplitude=1, offset=0, startTime=0, nPeriods=None, stopTime=None, collapse=True):
    if seed == None:
        seed=np.concatenate(([-1],np.ones(nBits-2,dtype='int'),[0]))
    
    genOptions = {3:[1,2,2],
                  4:[2,1,1,1],
                  5:[0,2,1,1,2],
                  6:[1,1,1,0,1,1],
                  7:[2,1,1,1,1,1,2],
                  8:[2,1,2,1,2,1,1,1]}
    if not nBits in genOptions:
        generator = np.zeros(nBits,dtype='int')
    else:
        generator = genOptions[nBits]
    mls = max_len_seq_ternary(seed, generator, bias)
    time, y = noise(mls=mls, freqHz=freqHz,amplitude=amplitude,offset=offset,startTime=startTime,nPeriods=nPeriods,stopTime=stopTime,collapse=collapse)
    return time, y

def mfbs():
    pass

#%% Main
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    

    time, y = prbs(freqHz=0.5, amplitude = 20, offset=80, startTime = 10, nPeriods=3, collapse=True)
    plt.plot(time,y,'o')
    
    time, y = prts(freqHz=0.5, amplitude = 20, offset=80, startTime = 10, nPeriods=3, collapse=True)
    plt.plot(time,y,'o')