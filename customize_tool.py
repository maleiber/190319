# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 21:12:13 2018

@author: 赵怀菩
"""
import numpy
import math
e_2=math.exp(2)
def Z_ScoreNormalization(x):
    mu=numpy.average(x)
    sigma=numpy.std(x)
    #x = (x - mu) / sigma;  
    x=[t-mu for t in x]
    x=[t/sigma for t in x]
    
    return x;  
#cos compares the differences between 2 point
def cos(vector1,vector2):  
    dot_product = 0.0;  
    normA = 0.0;  
    normB = 0.0;  
    for a,b in zip(vector1,vector2):  
        dot_product += a*b  
        normA += a**2  
        normB += b**2  
    if normA == 0.0 or normB==0.0:  
        #return None
        return 0
    else:  
        return dot_product / ((normA*normB)**0.5)  

def new_cos(vector1,vector2):  
    #vector is a array of i,
    #   and each of the i is dict
    #request the len of vector1 and 2 be the same
    cos_sum=0
    i=0
    key_list=vector1[i].get_attr()
    for i in range(len(vector1)):    
        v1=[vector1[i].get_by_attr(k) for k in key_list]
        v2=[vector2[i].get_by_attr(k) for k in key_list]
        value=cos(v1,v2)
        value=math.exp(value+1)/e_2
        value=4*(1-value)
        cos_sum=cos_sum+value
    return cos_sum
    
if __name__=='__main__':
    print (new_cos([{1:1,2:2},{1:2,2:3},{1:3,2:4}],[{1:1,2:2},{1:2,2:13},{1:3,2:74}]) )