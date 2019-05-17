# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:26:22 2019

@author: 赵怀菩
"""

import numpy as np
import struct
import matplotlib.pyplot as plt
import segment_mode

def build_pic_multi(im,im_sizex=28,im_sizey=28,window_size=3,step=1):
    #sizex is weight, sizey is high
    tstart=int(window_size/2)
    tstartx,tstarty=tstart,tstart
    tendx,tendy=im_sizex-tstart,im_sizey-tstart
    size_range=int(window_size/2)
    imarray=[]
    for x in range(tstartx,tendx):
        for y in range(tstarty,tendy):
            point=[]
            for i in range(-size_range,size_range+1):
                for j in range(-size_range,size_range+1):
                    point.append(im[y+i][x+j])
            imarray.append(point)
    
    multi_dimen_seg=[]
    i=0
    s=len(imarray[0])
    for x in imarray:
        multi_dimen_seg.append(segment_mode.multi_dimen_data(
                imarray[i],
                [str(i) for i in range(s)]))
        i=i+1
    return multi_dimen_seg
    pass

def time_trans_location(clu,im_sizex=26,im_sizey=26):
    ret_clu=[]
    for c in clu:
        now=[]
        center=c[0]
        lis=c[1]
        for i in lis:
            t=i[0]
            x=t%im_sizex
            y=int((t-x)/im_sizex)
            now.append([y+1,x+1])
        ret_clu.append(now)
    return ret_clu
    pass

if __name__=='__main__':
    filename='D:/zhp_workspace/190312/train-images.idx3-ubyte'
    with open(filename ,'rb') as f1:
        buf1 = f1.read() 
    image_index = 0
    image_index += struct.calcsize('>IIII')
    temp = struct.unpack_from('>784B', buf1, image_index) 
# '>784B'的意思就是用大端法读取784( 28*28 )个unsigned byte
    
    im = np.reshape(temp,(28,28))
    plt.imshow(im , cmap='gray')
    ar=build_pic_multi(im)
    
    co_seg=segment_mode.segment_mode(1,3, ar,'co',up_merge=False)
    co_seg.dc_factor=0.02
    co_seg.slide_cos_search(True)
    co_seg.density_clu(True)
    co_sequence=co_seg.build_pattern_of_symbol('co')
    clu=time_trans_location(co_seg.outer_clu)
    imn=im
    i=16
    for c in clu:
        for p in c:
            imn[p[1]][p[0]]=i
        i=i+1
    plt.imshow(imn , cmap='gray')
    pass