#!/usr/bin/env python
# coding: utf-8

from CoolProp.Plots import PropertyPlot
from CoolProp.CoolProp import PropsSI
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
    
def plotSeries_TS(data,time,cycles,labels,cycleColors,cycleCombined,saveDirectory,iTimeOffset=0,dpi=300):
    # Time sequence plot for State Points on T-S Diagram
    


    # Text box style for time indicator
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # Set medium
    medium = 'co2'

    # Set figure size 
    plt.rcParams["figure.figsize"] = (12,8)

    # Instantiate diagram
    diagram = PropertyPlot('co2', 'TS')
    diagram.calc_isolines()

    # Set colors so they do not repeat
    colors = sns.color_palette("hls", len(cycleCombined))

    # Time loop
    for iTime, tVal in enumerate(time):
        
        diagram.axis.set_prop_cycle('color', colors)
        
        # Cycle Loop
        for iCycle, cycle in enumerate(cycles):
            T = []
            p = []
            s = []
            for sensor in cycle:
                T.append(data['{}.T'.format(sensor)])
                p.append(data['{}.p'.format(sensor)])
                s.append(PropsSI('S','T',T[-1],'P',p[-1],medium))

            TT = np.array(T)
            ss = np.array(s)

            x = ss[:,iTime+iTimeOffset]/1000
            y = TT[:,iTime+iTimeOffset]

            u = np.diff(x)
            v = np.diff(y)
            pos_x = x[:-1] + u/2
            pos_y = y[:-1] + v/2
            norm = np.sqrt(u**2+v**2) 

            # Create lines with arrows
            diagram.axis.plot(x,y,cycleColors[iCycle])#,label=sensor)        
            diagram.axis.quiver(pos_x, pos_y, u/norm, v/norm, angles="xy", zorder=5, pivot="mid",scale=100)

            # Create state point plots
            for i, sensor in enumerate(cycle):
                if iCycle > 0 and i == 0:
                    pass
                elif iCycle > 0 and i == len(cycle)-1:
                    pass
                else:
                    diagram.axis.plot(x[i],y[i],'o',label=labels[iCycle][i],markersize=10,zorder=6)

        # Update the figure and save
        diagram.axis.legend(loc='upper left',prop={'family': 'monospace'})
        diagram.axis.set(xlabel='Specific Entropy [kJ/kg-K]');
        diagram.axis.set(ylabel="Temperature [K]")
        diagram.axis.text(0.5, 0.95, 'Time [day] = {:0.3f}'.format(tVal), transform=diagram.axis.transAxes, fontsize=14, ha='center', va='top', bbox=props)

        diagram.figure
        diagram.savefig('{}/time_TS/{}.png'.format(saveDirectory,iTime+iTimeOffset),dpi=dpi)
        diagram.axis.clear()
        
      
def plotSeries_SvsM(iTimes,time,W_setpoint,W_measured,saveDirectory,dpi=300):
    
    # Text box style for time indicator
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
       
    for iTime in iTimes:
        tVal = time[iTime]
        
        fig,ax = plt.subplots(figsize=(6,3))
        ax.plot(time,W_setpoint,'k-',label='Setpoint')
        ax.plot(time[:iTime],W_measured[:iTime],'r--',label='Simulation',linewidth=0.75)
        plt.axvline(x=time[iTime],color='fuchsia',linewidth='0.75')
    
        ax.legend(fontsize='large',loc='lower left')
        ax.set(ylabel='Power [MW]');
        ax.set(xlabel="Time [days]")
    
        ax.text(0.85, 0.1, 'Time [day] = {:0.3f}'.format(tVal), transform=ax.transAxes, fontsize=8, ha='center', va='top', bbox=props)
    
        ax.grid(axis='x')
    
        plt.tight_layout()
        fig.savefig('{}/time_SvsM/{}.png'.format(saveDirectory,iTime),dpi=dpi)
        fig.clear()