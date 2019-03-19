# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 12:32:11 2018

@author: 赵怀菩
"""
import random
import math
import numpy as np
from draw_pic import *
import time

class data_builder(object):
    def __init__(self,min_x_value,max_x_value,length,random_factor=0.002,commonfactor=1):
        self.xlist=[]
        self.rare_list=[]
        self.randomlize_xlist=[]
        self.min_x=min_x_value
        self.max_x=max_x_value
        self.length=length
        self.random_factor=random_factor
        self.common=commonfactor
        self.build_array()
        #self._build_random_array()
                   
            
        #
    def build_array(self):
        #build a sin array
        if self.length<240:
            print ('too small array: at least 240')
            return
        a=[x for x in range(self.length)]
        #a is xaxis
        b=self.max_x-self.min_x
        k=b/2
        
        b=[(math.sin(i/12)+1)*k+self.min_x for i in a]
        self.xlist=b
        self.randomlize_xlist=b
        #b is value in yaxis
        pass
    def _build_random_array(self,array=False,start=0,end=False,change_randomlize_array=True,do_shift=True):
        #start and end of this index
        #random value is expand of the random series
        if self.length<240:
            print ('too small array: at least 240')
            return
        if array==False:
            array=self.xlist
        if end==False:
            end=self.length
            
        temp_array=[]
        if end-start<1:
            return
        rand=np.random.normal(size=end-start)
        for i in range(end-start):
            if abs(rand[i])>0.04:
                #too common ,not changes
                temp=((rand[i]*self.random_factor)+1)*array[start+i]
                temp_array.append(temp)
            else:
                temp_array.append(array[start+i])
        
        #then do the total len change
        randb=np.random.normal(size=end-start)
        now=start
        dx=self.max_x-self.min_x
        for i in range(end-start):
            if abs(randb[i])<1.5:
                pass
            elif i+start>=now:
                #start line change
                blocklength=int(rand[i]*0.6+100)
                blocklength=min(blocklength,end-i)
                blockshift=randb[i]*0.05*dx
                for j in range(blocklength):
                    if do_shift==True:
                        temp_array[i+j]=temp_array[i+j]+blockshift
                now=now+blocklength
        if change_randomlize_array==True:
            self.randomlize_xlist=temp_array
        return temp_array
    def add_rare(self,complexity,length,pos=[],posi_num=2):
        #complexity determind how long the rare array
        #length is how long rare sequence is
        #position is where rare sequence start in array
        #for some reasons we regard rare sequence which appear at least 2 times
        #    so 2 position needed
        rarelength=length*self.common*random.uniform(0.8,1.3)
        rarelength=int(rarelength)
        min_std=0.37*math.sqrt(complexity)
        max_std=0.91*math.sqrt(complexity)
        position=pos
        while True:
            rare_array=self.__form_rare(complexity,rarelength)
            if self._verify_rare_sequence(rare_array,min_std,max_std)==True:
                break
        #now get an effective rare sequence , but need to shift
        array_avg=self.min_x+(self.max_x-self.min_x)/2
        rare_avg=np.average(rare_array)
        shiftvalue=rare_avg-array_avg
        
        a=[x for x in range(len(rare_array))]
        draw_pic(rare_array,False,a)
        rare_array=[rarevalue-shiftvalue for rarevalue in rare_array]
        
        #then add rare sequence in the randomlize array
        #    it need at least 2 position. if not mentioned above, create 2.
        #print ('check len of position:',position)
        while len(position)<posi_num:
            
            randnumber=int(random.uniform(0,self.length)%(self.length-rarelength))
            #print ('time seed', timeseed,'randnumber:',randnumber)
            position.append(randnumber)
            #dont know why it is always same
            #add a seed of clock
            #problem solved
            #dont know why the default parametre can last in next time
        
        #print ('form rare position:',position)

#        position.sort()
#        detla_position=[]
#        i=1
#        detla_position.append(position[0])
#        while i<len(position):
#            detla_position.append(position[i]-position[i-1])
#            i=i+1
#        i=0

        #store the rare to list  with position information
        self.rare_list.append([position,rare_array])
        position=[]
        # [0] is position the rare seq add in ,[1] is the seq
            
    def insert_rare_in_rlist(self):
        position_lis=[]
        #it has: [position,array]
        #seprare the dual group of position and array
        #make each position and array a pair
        #each of its element:
        #    before: [[pos1,pos2,...],rare_array],...
        #    after:  [pos1,rare_array],[pos2,rare_array],...
        for rarei in self.rare_list:
            for p in rarei[0]:
                position_lis.append([p,rarei[1]])
        #use new pair list: position_lis
        
        #sort position and caculate the difference between each and its next element
        #    in order to make correctly insert 
        #    when finished an insert, the following index of insert position differ. 
        position_lis=sorted(position_lis,key=lambda pos_and_array:pos_and_array[0])
        detla_position=[]
        i=1
        detla_position.append(position_lis[0][0])
        while i<len(position_lis):
            
            detla_position.append(position_lis[i][0]-position_lis[i-1][0])
            i=i+1
        print ('pos list:',position_lis)
        print ('detla list:',detla_position)
        i=0
        now=0
        for i in range(len(position_lis)):
            now=now+detla_position[i]
            #when splice ,the rare sequence 
            #randomlize the rare array
            rare_array=position_lis[i][1]
            
            #insert_rare_array=self._build_random_array(rare_array,0,len(rare_array),False,False)
            insert_rare_array=rare_array
            
            self.randomlize_xlist[now:now]=insert_rare_array
            now=now+len(position_lis[i][1])
        pass        
    
    def __form_rare(self,complexity,length):
        #complexity determind how long the rare array
        #length is how long rare sequence is
        raw_array=[]
        rare_array=[]
        iter_time=max(2,int(math.sqrt(complexity)))
        for j in range(iter_time):
            
            standardA=self.max_x-self.min_x
            standardA=self.min_x+max(min(0.1,standardA*0.1),standardA*random.random())
            standardA=0.5*standardA/iter_time
            
            for i in range(int(complexity)):
                standardw=1/(j+1)*random.uniform(0.005,40)
                standardw=1/standardw
                standardfai=random.uniform(0.7,1.2)*length
                standardfai=random.uniform(0.7,1.2)*math.sqrt(standardfai)
                raw_array.append(self._build_sin(standardA*random.uniform(0.55,1.5),standardw,standardfai,self.length))
                pass
        
        for j in range(length):
            rare_array.append(0)
            for i in range(int(complexity)):
                rare_array[j]=rare_array[j]+raw_array[i][j]
        return rare_array
    def _verify_rare_sequence(self,rare_array,min_std,max_std):
        tempstd=np.std(rare_array)
        print (tempstd)
        if tempstd>=min_std and tempstd<=max_std:
            return True
        else:
            return False
        
    def _build_sin(self,A,w,fai,length,dx=1/12):
        #f(x)=Asin(wx+fai)
        a=[x for x in range(length)]
        #a is xaxis
        b=[A*(math.sin(i*dx*w+fai)) for i in a]
        #print ('A:',A,' w:',w,'fai:',fai)
        return b
        pass
        
        
    
if __name__=='__main__':
    b=data_builder(20,30,1000,0.025,1)
    a=[x for x in range(1000)]
    draw_pic(b.randomlize_xlist,False,a)
    
    b.add_rare(100,80)
    b.add_rare(100,120)
    b.insert_rare_in_rlist()
    a=[x for x in range(len(b.randomlize_xlist))]
    draw_pic(b.randomlize_xlist,False,a)        
    
    pass