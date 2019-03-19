# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 08:36:30 2018

@author: 赵怀菩
"""
import pandas as pd
import matplotlib.pyplot as plt
import random
import math

class draw_pic(object):
    def __init__(self,yarray,xcolor=False,xarray=False,draw_line=True,save_name='',title='',text_data=False,y_is_multi=False):
        #value of yarray is necessary
        #print (yarray,xcolor,xarray)
        fig,ax = plt.subplots()
        fig.set_size_inches(248.5, 10.5)
        ax.grid(True)
        a=yarray
        v_min=120
        v_max=250
        
        plt.tick_params(labelsize=64)  
        labels = ax.get_xticklabels() + ax.get_yticklabels()  
        [label.set_fontname('Times New Roman') for label in labels]
        
        #cm = plt.cm.get_cmap('RdYlBu')
        cm = plt.cm.get_cmap('brg')
        if type(xcolor)==bool:
            z=[250 for i in yarray]
        else:
            z=xcolor
            v_min=min(z)
            v_max=max(z)
        
        if type(xarray)==bool :
            b=[i for i in range(len(yarray))]
        else:
            b=xarray
        if y_is_multi==True:
            key_list=a[0].get_attr()
            a={k:[] for k in key_list}
            for i in yarray:
                for k in a:
                    a[k].append(i.get_by_attr(k))
            for k in a:
                sc = plt.scatter(b, a[k], c=z, vmin=v_min, vmax=v_max, s=35, cmap=cm)
                #z=[x-16 for x in z]
        else:
            sc = plt.scatter(b, a, c=z, vmin=v_min, vmax=v_max, s=35, cmap=cm)
        if draw_line==True:
            if y_is_multi==True:
                for k in a:
                    ax.plot(b,a[k],alpha=0.6,linewidth=6)
            else:
                ax.plot(b,a,alpha=0.6,linewidth=12)
        plt.colorbar(sc)
        if len(title)<1:
            pass
        else:
            plt.title(title)
        if type(text_data)==bool:
            pass
        else:
            #[(x,y),str1],...
            for p in text_data:
                x,y=p[0]
                tempstr=p[1]
                plt.text(x,y,tempstr,size=84)
        if len(save_name)>0:
            save_name=save_name+'.png'
            plt.savefig(save_name, dpi=30)
        
        plt.show()
        pass

class draw_sca(object):
    def __init__(self,x,y,alpha=False):
        fig,ax = plt.subplots()
        fig.set_size_inches(12,12)
        ax.grid(True)
        a=x
        b=y
        cm = plt.cm.get_cmap('RdYlBu')
        z=[1 for i in range(len(x))]
        if alpha==False:
            pass
        else:
            pass
        
        
        sc = plt.scatter(b, a, c=z,alpha=0.3,vmin=0, vmax=1256, s=35, cmap=cm)
        plt.colorbar(sc)
        plt.show()
        pass
    pass
if __name__ == '__main__':
    a=[x for x in range(500)]
    #a is xaxis
    b=[math.sin(i/12) for i in a]
    #b is value in yaxis
    z=[random.randint(0,255) for i in a]
    #z is color of each point
    sc = plt.scatter(a, b, c=z, vmin=0, vmax=256, s=35, cmap=cm)
    x=[1,2,3,5]
    y=[11,12,13,24]
    xcolor=[20,20,232,223]
    draw_pic(x)
    draw_pic(x,xcolor)
    draw_pic(x,xcolor,y)
    draw_pic(x,xcolor,y,False)
        