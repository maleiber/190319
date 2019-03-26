# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 21:09:56 2018

@author: 赵怀菩
"""
from customize_tool import *
from FP_tree import *

import draw_pic
import data_builder
import math
import random
import sys
import time
sys.path.append("D:/zhp_workspace.180125")
from main import *

class multi_dimen_data(object):
    """
    it is a point of multi data
    multi data in a point stand for each point have several information
    each of data should have value&name, cannot be empty
    """
    def __init__(self,mult=[],attrname=''):
        self.data={}
        for name in attrname:
            self.data[name]=mult[0]
            mult.pop(0)
        
        pass
    def set_by_attr(self,name,value):
        self.data[name]=value
        return
    def get_by_attr(self,name):
        return self.data[name]
    def get_all_value(self):
        #give all value by original order cannot find key message
        return [self.data[k] for k in self.data]
    def get_attr(self):
        return [k for k in self.data]
    def __gt__(self,other):
        attrlist=[k for k in self.data]
        m1=max([self.data[k] for k in attrlist])
        m2=max([other.data[k] for k in attrlist])
        return m1>m2
    def __mul__(self,scalar):
        attrlist=[k for k in self.data]
        return multi_dimen_data([self.data[k]*scalar for k in attrlist],attrlist)
    def __truediv__(self,scalar):
        attrlist=[k for k in self.data]
        return multi_dimen_data([self.data[k]/scalar for k in attrlist],attrlist)
    
    def __add__(self,other):
        #the key  will refer the former 'self'
        #add by same key
        attrlist=[k for k in self.data]
        return multi_dimen_data([self.data[k]+other.get_by_attr(k) for k in attrlist],attrlist)
        #return sum([self.data[k]+other.data[k] for k in self.data])
    def __sub__(self,other):
        attrlist=[k for k in self.data]
        return multi_dimen_data([self.data[k]-other.get_by_attr(k) for k in attrlist],attrlist)
    def __add_by_sum(self,other):
        s1=sum([self.data[k] for k in self.data])
        s2=sum([other.get_by_attr(k) for k in other.data])
        return s1+s2
    def __sub_by_sum(self,other):
        #subminus by same key, and return value by sum of all submission
        return sum([self.data[k]-other.get_by_attr(k) for k in self.data])
    def show(self):
        for k in self.data:
            print(k,':',self.data[k],' ')

class segment_mode(object):
    """
    data_array:in this time, the data is multidimen data
    """
    def __init__(self,minl,maxl,data_array,name='',blurry=True,standardlize=True,up_merge=True):
        self.name=name
        self.min_len=minl
        self.max_len=maxl
        self.dataseq=data_array
        self.data_sign=[]
        self.sub_seq_information=[]
        self.sub_dict={}
        self.color_value=[]
        if blurry==True:
            self._blurry()
        if standardlize==True:
            self._standardlize()
        if up_merge==True:
            self._bottom_up_merge()
        else:
            self.data_sign=[x[0]for x in self.dataseq]
        pass
    def _blurry(self):
        
        new_seq=[   #int(
                        (self.dataseq[max(i-3,0)]+
                        self.dataseq[max(i-2,0)]+
                        self.dataseq[max(i-1,0)]+
                        self.dataseq[i]+
                        self.dataseq[min(i+1,len(self.dataseq)-1)]+
                        self.dataseq[min(i+2,len(self.dataseq)-1)]+
                        self.dataseq[min(i+3,len(self.dataseq)-1)]
                        )/7
                    #)
                    for i in range(len(self.dataseq))
                ]
        
        self.dataseq=new_seq
            
        pass
    def _standardlize(self):
        self.attr_list=self.dataseq[0].get_attr()
        self.value_list={k:[] for k in self.attr_list}
        for i in self.dataseq:    
            for k in self.attr_list:
                self.value_list[k].append(i.get_by_attr(k))
        for k in self.attr_list:       
            self.value_list[k]=Z_ScoreNormalization(self.value_list[k])
        newseq=self.dataseq
        for i in range(len(self.dataseq)):
            for k in self.attr_list:
                newseq[i].set_by_attr(k,self.value_list[k][i])
            
        
        self.dataseq=newseq
                
        #self.dataseq=Z_ScoreNormalization(self.dataseq)
        pass
    def __build_origin_segment(self):
        self.data_sign=[x for x in self.dataseq]
#        prev=self.dataseq[0]
#
#        #self.data_sign.append(prev)
#        for i in range(len(self.dataseq)-1):
#            now=self.dataseq[i]
#            self.data_sign.append([[prev,now],now-prev])
#            prev=now
#        #finished dx
        a=[i for i in range(len(self.data_sign))]
        outputname='origin_seg_'
        outputname=outputname+self.name
        draw_pic.draw_pic(self.data_sign,False,a,save_name=outputname,y_is_multi=True)
        pass
    def _bottom_up_merge(self):
        self.__build_origin_segment()
        # self.data_sign is the origin segment
        # now segment
        threshold=6
        global_threshold=12
        zipshold=0.2
        now_segment=[]
        #element in now segment:
        #    [[point,...],diff]
        #when try to merge now and next:
        #    make point became [nowpoint_start,...,nowpoint_end,nextpointstart,...,nextpointend]
        #    new segment=(next_end - now_start,data_sign[next_end]-data_sign[now_start])
        #    in per dx, step of newsegment is (y/x)  
        #if size of point <=2, diff=0
        #    diff=sum[ abs((p-nowstart)*step-(data[p]-data[nowstart])) for p in point[1:-1] ]
        #                                                                   *expect start and end
        #make now seg init
        for i in range(len(self.data_sign)):
            now_segment.append([[i],0])
        #start iter
        
        #one treverse
        while True:
            alternate_seg=[]
            i=0
            direct_merge_count=0
            while i<len(now_segment)-1:
                now_p,nowdiff=now_segment[i]
                next_p,nextdiff=now_segment[i+1]
                diff={}
                new_p=now_p+next_p
                #caculate diff
                if len(new_p)<=2:
                    diff={}
                elif len(new_p)>self.max_len:
                    # long than max window's width
                    #cannot use
                    diff={'__':threshold}
                else:
                    #cacul segment by now_p and next_p
                    x,y=self.__caculate_seg(now_p,next_p)
                    #there have multi-dimen of step
                    #y ismultiple
                    #step=y/x
                    step={k:y.get_by_attr(k)/x for k in y.get_attr()}
                    nowstart=new_p[0]
                    '''diff=sum([abs(
                                (p-nowstart)*step -(self.data_sign[p]-self.data_sign[nowstart])
                                )
                                for p in new_p[1:-1]
                            ])
                    '''
                    
                    diff={k:0 for k in y.get_attr()}
                    
                    for k in diff:
                        diff[k]=sum([abs(
                                (p-nowstart)*step[k] -(self.data_sign[p].get_by_attr(k)-self.data_sign[nowstart].get_by_attr(k))
                                )
                                for p in new_p[1:-1]
                            ])
                all_diff_is_zero=True
                all_diff_under_single_thres=True
                for k in diff:
                #judge if merge by diff
                    if diff[k]!=0:
                        all_diff_is_zero=False
                    if diff[k]>threshold:
                        all_diff_under_single_thres=False
                        
                if all_diff_is_zero==True:        
                    #when diff =0 direct change now segment
                    now_segment.pop(i)
                    now_segment[i]=[new_p,diff]
                    direct_merge_count=direct_merge_count+1
    
                elif all_diff_under_single_thres==True:
                    #added to alternate_seg
                    sumdiff=sum([diff[k] for k in diff])
                    if sumdiff<global_threshold:
                        alternate_seg.append([i,new_p,diff,sumdiff])
                #now=next
                i=i+1
            #sorted and chose
            zip_rate=len(now_segment)/len(self.data_sign)
            #print ('zip_rate',zip_rate,'alter:',alternate_seg)
            if len(alternate_seg)>0 and zip_rate>zipshold:
                alternate_seg=sorted(alternate_seg,key=lambda x:x[3])
                #chose one smallest diff
                i,new_p,diff,sumdiff=alternate_seg[0]
                
                #merge
                now_segment.pop(i)
                now_segment[i]=[new_p,diff]
            elif direct_merge_count==0:
                #no more alter_seg  or zip rate pass,break
                break
        #cacul the difference now&next in each of the now segment
        # if difference: <threshold , directly merge it in now segment
        # if not ,merge 1 the lowest in each traverse until zip rate pass
        #  however, the origin length of now segment could not more than w
        #all segment merge finish,then update data_sign
        new_sign=[self.data_sign[0]]
        #the first value always not changed
        
        self.data_sign_match_origin_dict={}
        i=0
        for now_p,diff in now_segment:
            self.data_sign_match_origin_dict[i]=now_p
            new_sign.append(self.data_sign[now_p[-1]])
            i=i+1
            pass
        #take a picture
        a=[x for x in range(len(new_sign))]
        outputname='af_merge_seg_'
        outputname=outputname+self.name
        draw_pic.draw_pic( new_sign,a,a,save_name=outputname,y_is_multi=True)
        self.data_sign=new_sign
        
        pass
    def __caculate_seg(self,now_p,next_p):
        new_p=now_p+next_p
        x=new_p[-1]-new_p[0]
        y=self.data_sign[new_p[-1]]-self.data_sign[new_p[0]]
        return (x,y)
        pass
    def slide_cos_search(self,draw=False):
        
        #get all sub
        w=self.min_len
        #attention that w =1 ,would not use the min_len
        #w at least be 1 or it will made error
        #w=1
        for i in range(len(self.data_sign)):
            start=i
            end=i+w
            
            if end+1>=len(self.data_sign):
                #goal sub exceed
                break
            sub_seq=self.data_sign[start:end]
            sub_key=(tuple(sub_seq))
            self.sub_dict[sub_key]=[start,end]
        #the goal subseq is after now, before has been found.
        
        self.sub_cos={}
        e_2=math.exp(2)
        #calulate cos of all sub
        for p1 in self.sub_dict:
            s1,e1=self.sub_dict[p1]

            #neighborhood of s1,e1
            for p2 in self.sub_dict:
                s2,e2=self.sub_dict[p2]
                
                if s2!=s1:
                    sub1=self.data_sign[s1:e1]
                    sub2=self.data_sign[s2:e2]
                    #value=L2_distance(sub1,sub2)
                    value=new_cos(sub1,sub2)
                    #range is(-1,1)
                    #closer to one ,more similar
                    #self.sub_cos[(s1,e1,s2,e2)]=value
                    
                    #value=math.exp(value+1)/e_2
                    #however the goal is get 'distance' between 2 point
                    #value=4*(1-value)
                    self.__add_sub_value((s1,e1),(s2,e2),value)
        #caculate cos finish
        #caculate d_c
        dc=self.__count_dc_of_cos_dict()
        #caculate density
        density_set=[]
        for p1 in self.sub_dict:
            s1,e1=self.sub_dict[p1]
            
            neighborhood=0
            #neighborhood of s1,e1
            for p2 in self.sub_dict:
                s2,e2=self.sub_dict[p2]
                
                if s2>e1 or s1>e2:
                    sub1=self.data_sign[s1:e1]
                    sub2=self.data_sign[s2:e2]
                    value=self.__get_sub_value((s1,e1),(s2,e2))
                    
                    neighborhood=neighborhood+math.exp(-(value/dc)*(value/dc))
                    #value is smaller, p is bigger . wanted
            density_set.append([(s1,e1),neighborhood])
        #density finish ,then sort
        density_set=sorted(density_set,key=lambda x:x[1])
        #print('density:',density_set)
        x_array=[x[0][0] for x in density_set]
        y_array=[x[1] for x in density_set]
        t_array=[x for x in x_array]
        #all fin
        #print('theta')
        #draw_pic.draw_pic( y_array,t_array,x_array,False)
        
        
        self.data_rou_theta=[]
        i=0
        max_theta=0
        
        for pair in density_set:
            s1,e1=pair[0]
            neighborhood=pair[1]
            min_theta=999
            if i+1<len(density_set):
                #forget to except the start place
                # it cannot repeat in same time
                for next_pair in density_set[i+1:]:
                    #compare with all rou> now
                    s2,e2=next_pair[0]
                    if s2!=s1:
                        
                        min_theta=min(min_theta,self.__get_sub_value((s1,e1),(s2,e2)))
                    pass
                max_theta=max(max_theta,min_theta)
                self.data_rou_theta.append([(s1,e1),neighborhood,min_theta])
            else:
                self.data_rou_theta.append([(s1,e1),neighborhood,max_theta])
                #the last one
                break
            #forget i=i+1
            i=i+1
        #standardlize
        x_array=[x[1] for x in self.data_rou_theta]
        x_array=Z_ScoreNormalization(x_array)
        minx=min(x_array)
        x_array=[x-minx for x in x_array]
        
        y_array=[x[2] for x in self.data_rou_theta]
        y_array=Z_ScoreNormalization(y_array)
        miny=min(y_array)
        y_array=[y-miny for y in y_array]
        
        
        t_array=[x[0][0] for x in self.data_rou_theta]
        for i in range(len(self.data_rou_theta)):
            rou=x_array[i]
            theta=y_array[i]
            gamma=rou*theta
            self.data_rou_theta[i]=[self.data_rou_theta[i][0],rou,theta,gamma]
        #all fin
        #print('x_array',x_array,'len',len(x_array))
        #print('x_array',y_array,'len',len(y_array))
        outputname='rou_theta_'
        outputname=outputname+self.name
        if draw==True:
            draw_pic.draw_pic( y_array,t_array,x_array,False,save_name=outputname)
        pass
    def get_mid_d(self):
        value_seq=[]
        
        for k1 in self.sub_cos:
            sub_dict=self.sub_cos[k1]
            for k2 in sub_dict:
                value_seq.append(sub_dict[k2])
        t=0.5*len(value_seq)
        t=round(t)
        t=max(t,1)
        value_seq.sort()
        
        #print('value seq:', value_seq)
        #print('t=',t)
        return value_seq[t]
    def get_var_d(self):
        value_seq=[]
        
        for k1 in self.sub_cos:
            sub_dict=self.sub_cos[k1]
            for k2 in sub_dict:
                value_seq.append(sub_dict[k2])
        return numpy.var(value_seq)
    def __count_dc_of_cos_dict(self):
        value_seq=[]
        
        
        for k1 in self.sub_cos:
            sub_dict=self.sub_cos[k1]
            for k2 in sub_dict:
                value_seq.append(sub_dict[k2])
        t=self.dc_factor*len(value_seq)
        t=round(t)
        t=max(t,1)
        value_seq.sort()
        
        #print('value seq:', value_seq)
        #print('t=',t)
        self.dc=value_seq[t]
        return value_seq[t]
        pass
    def __get_sub_value(self,seg1,seg2):
        s1,e1=seg1
        s2,e2=seg2
        seg1_dict={}
        
        if self.sub_cos.get((s1,e1))==None:
            #not exist
            print (s1,',',e1,' not exist')
            return 0
        else:
            seg1_dict=self.sub_cos.get((s1,e1))
        if seg1_dict.get((s2,e2))==None:
            #not exist
            print (s2,',',e2,' not exist')
            return 0
        else:
            return seg1_dict[(s2,e2)]
        pass
    
    def __add_sub_value(self,seg1,seg2,val):
        s1,e1=seg1
        s2,e2=seg2
        seg1_dict={}
        seg2_dict={}
        if self.sub_cos.get((s1,e1))==None:
            seg1_dict={}
        else:
            seg1_dict=self.sub_cos.get((s1,e1))
        if seg1_dict.get((s2,e2))==None:
            seg1_dict[(s2,e2)]=val
        else:
            pass
            #error. had been added
        self.sub_cos[(s1,e1)]=seg1_dict    
        
        if self.sub_cos.get((s2,e2))==None:
            seg2_dict={}
        else:
            seg2_dict=self.sub_cos.get((s2,e2))
        if seg2_dict.get((s1,e1))==None:
            seg2_dict[(s1,e1)]=val
        else:
            pass
            #error. had been added
        self.sub_cos[(s2,e2)]=seg2_dict   
        
        pass
    def build_pattern_of_symbol(self,unique_string):
        #unique string is important to differ this time sequence and other
        pattern_of_symbol=[]
        '''
        each index of pattern of symbol:
        pair[0]:start index in data_sign, and also the clustering center. like 3 (only start index recorded.)
        pair[1]:next time point of pattern, use a tuple to organized. like (1,2,4,5,3), it have pair[0] but it is in the end
        pair[2]:the value of clustering center in data_sign
        pair[3]:start index of clustering center in dataseq(origin data), like[5,6]
        pair[4]:other point in this cluster in dataseq,    like[[1,2],[3,4],[7,8],[9,10,11]]. sum with pair[3] may not be all seq,
           and, each point should include at least 1 point in dataseq. the upsize and each size of 1 point is not required the same size 
        to see how point in data_sign represent in dataseq, see:
            self.data_sign_match_origin_dict[i of data_sign(1 point)]=[1,2,3,...means point in dataseq]
            if want to make several point in data_sign, use it repeatly and splice and answer.
        !!! In pair[0] and pair[1] there are only start index recorded now. if want to avoid time overlap(maybe?maynot?)
            when get intersection of 2 time duration, you can made pair[0] and pair[1] record start and end time.
        *** you can also get pair[5] as the value of clustering center in dataseq, but thus it will made each index too large.
            in fact, with pair[3] and pair [4] it became large already.
        '''
        start_record=[]
        for pair in self.outer_clu:
            s1,e1=pair[0]
            all_start=[x[0] for x in pair[1]]
            key_array=[x[0] for x in pair[1]]
            key_array.insert(0,unique_string)
            hash_key=tuple(key_array)
            #all_start.append(s1)
            #all start position of this cluster
            
            temp_list=[]
            clu_center_in_dataseq=[]
            temp_list=[self.data_sign_match_origin_dict[s1]]
            if s1!=e1:
                for i in range(s1+1,e1+1):
                    temp_list.append(self.data_sign_match_origin_dict[i])
            clu_center_in_dataseq.append(temp_list)
            #we think s1,e1 is a continues time in data_sign, so will in dataseq, so we shouldn't separate
            #the time. if it is [1,2,3], it will mean [1,2,3,4,5,6] there, not [[1,2],[3,4],[5,6]].
            #each the element in pair[1] is like this.
            point_data_sign_in_dataseq=[]
            temp_list=[]
            for s2,e2 in pair[1]:
                temp_list=[self.data_sign_match_origin_dict[s1]]
                if s2!=e2:
                    for i in range(s2+1,e2+1):
                        temp_list.append(self.data_sign_match_origin_dict[i])
                point_data_sign_in_dataseq.append(temp_list)
            for start in all_start:
                if start not in start_record:
                    pattern_of_symbol.append([start,hash_key,pair[2],clu_center_in_dataseq,point_data_sign_in_dataseq])
                    start_record.append(start)
            pass
        
        for pair in self.inner_clu:
            s1,e1=pair[0]
            all_start=[x[0] for x in pair[1]]
            key_array=[x[0] for x in pair[1]]
            key_array.insert(0,unique_string)
            hash_key=tuple(key_array)
            #all_start.append(s1)
            #all start position of this cluster
            temp_list=[]
            clu_center_in_dataseq=[]
            temp_list=[self.data_sign_match_origin_dict[s1]]
            if s1!=e1:
                for i in range(s1+1,e1+1):
                    temp_list.append(self.data_sign_match_origin_dict[i])
            clu_center_in_dataseq.append(temp_list)
            #we think s1,e1 is a continues time in data_sign, so will in dataseq, so we shouldn't separate
            #the time. if it is [1,2,3], it will mean [1,2,3,4,5,6] there, not [[1,2],[3,4],[5,6]].
            #each the element in pair[1] is like this.
            point_data_sign_in_dataseq=[]
            temp_list=[]
            for s2,e2 in pair[1]:
                temp_list=[self.data_sign_match_origin_dict[s1]]
                if s2!=e2:
                    for i in range(s2+1,e2+1):
                        temp_list.append(self.data_sign_match_origin_dict[i])
                point_data_sign_in_dataseq.append(temp_list)
            for start in all_start:    
                if start not in start_record:
                    pattern_of_symbol.append([start,hash_key,pair[2],clu_center_in_dataseq,point_data_sign_in_dataseq])
                    start_record.append(start)
            
            pass
        pattern_of_symbol=sorted(pattern_of_symbol,key=lambda x:x[0])
        self.pattern_symbol=pattern_of_symbol
        
        return self.pattern_symbol
        pass
    
    def density_clu(self,draw=False,inner=8,outlier=1,mark_outlier=True):
        #self.data_rou_theta[i]=[(s1,e1),rou,delta,gamma]
        self.data_rou_theta=sorted(self.data_rou_theta,key=lambda x:x[3],reverse=True)
        clu_center=[]
        #clu_center record inner
        out_center=[]
        #out record outer
        match_data_sign=[]
        #data of clustering center
        inner_clu_threshold=inner
        outer_clu_threshold=outlier
        if_partition={}
        for key in self.sub_cos:
            s1,e1=key
            for i in range(s1,e1):    
                if_partition[i]=False
        #max_e=len(if_partition)-1
        #record inner
        self.min_delta=999
        for pair in self.data_rou_theta:
            if pair[3]>=inner_clu_threshold:
                self.min_delta=min(pair[2],self.min_delta)
                s1,e1=pair[0]
                match_data_sign=self.data_sign[s1:e1]
                s1e1_done=False
                now_center=(s1,e1)
                now_clu=[]
                #judge all have distance with center
                if self.sub_cos.get((s1,e1))==None:
                    seg1_dict={}
                else:
                    seg1_dict=self.sub_cos.get((s1,e1))
                for i in range(s1,e1):   
                    if i in if_partition and if_partition[i]==True:
                        #has been divide
                        s1e1_done=True
                        break  
                if s1e1_done==True:
#                    print (str(s1)+' used s1')
                    continue
#                print (str(s1)+'-'+str(e1)+'un used s1')
                
                for key in seg1_dict:
                    s2,e2=key
                    if s2>e1 or s1>e2:
                        s2e2_done=False
                        
                        for i in range(s2,e2):  
                            if i in if_partition and if_partition[i]==True:
                                #has been divide
                                s2e2_done=True
                                break
                        if s2e2_done==True:
#                            print (str(s2)+' used s2')
                            continue
#                        print (str(s1)+'-'+str(e1)+' and '+str(s2)+'-'+str(e2)+' can used')
                        if seg1_dict[key]<=self.dc:
                            #add to this clu
                            now_clu.append(key)
                            for i in range(s2,e2):    
                                if_partition[i]=True
                                
                            for i in range(s1,e1):    
                                if_partition[i]=True
                        else:
#                            print (' not passed')
                            pass
                            #had been divided
                #often match at least appearence 2 times
                if len(now_clu)>1:
                    clu_center.append([now_center,now_clu,match_data_sign])
            else:
                pass
                #not in clu_center is outlier
        #outter can same with inner
        for i in if_partition:
            if_partition[i]=False
        
        if mark_outlier==True:
            #recode outer
            for pair in self.data_rou_theta:
                if pair[3]<outer_clu_threshold:
                    s1,e1=pair[0]
                    match_data_sign=self.data_sign[s1:e1]
                    s1e1_done=False
                    now_center=(s1,e1)
                    now_clu=[]
                    #judge all have distance with center
                    if self.sub_cos.get((s1,e1))==None:
                        seg1_dict={}
                    else:
                        seg1_dict=self.sub_cos.get((s1,e1))
                    for i in range(s1,e1):   
                        if i in if_partition and if_partition[i]==True:
                            #has been divide
                            s1e1_done=True
                            break  
                    if s1e1_done==True:
                        continue
                    for key in seg1_dict:
                        s2,e2=key
                        if s2>e1 or s1>e2:
                            s2e2_done=False
                            for i in range(s2,e2):   
                                if i in if_partition and if_partition[i]==True:
                                    #has been divide
                                    s2e2_done=True
                                    break
                            if s2e2_done==True:
                                continue
                            if seg1_dict[key]<=self.dc:
                                #add to this clu
                                now_clu.append(key)
                                for i in range(s2,e2):    
                                    if_partition[i]=True
                                for i in range(s1,e1):    
                                    if_partition[i]=True
                                #had been divided
                    if len(now_clu)>1:
                        out_center.append([now_center,now_clu,match_data_sign])
                else:
                    pass
            pass
        
        self.inner_clu=clu_center 
        self.outer_clu=out_center
        
        #time to show
        y_array=self.data_sign
        x_array=[x for x in range(len(y_array))]
        y_pos=max(y_array)
        key_list=y_pos.get_attr()
        y_pos=max([y_pos.get_by_attr(k) for k in key_list])
        y_pos=y_pos + 0.1
        #print ('inner cluster num:',len(self.inner_clu))
        #print (self.inner_clu)
        max_clu=len(self.inner_clu)
        clu_array=[0 for x in x_array]
        loc_mark=[]
        nowcolor=0
        for pair in self.inner_clu:
            color_array=[]
            color_array=pair[1]
            color_array.append(pair[0])
            #each segment
            if len(color_array)<2:
                continue
            for p in color_array:
                s1,e1=p
                #fill (s1,e1)
                #s1 is x
                #y_array[s1]+0.1 is y
                #nowcolor is text
                loc_mark.append([(s1,y_pos),str(nowcolor)])
                for i in range(s1,e1):
                    clu_array[i]=nowcolor
            #for next time color changed
            nowcolor=nowcolor+1
        clu_array=[nowcolor*2 if x==max_clu else x for x in clu_array]
        outputname='frequent_sequence_'
        outputname=outputname+self.name
        if draw==True:
            draw_pic.draw_pic( y_array,clu_array,x_array,save_name=outputname,title=self.name,text_data=loc_mark,y_is_multi=True)
        
        
        #print ('outter cluster num:',len(self.outer_clu))
        #print (self.outer_clu)
        max_clu=len(self.outer_clu)
        clu_array=[max_clu for x in x_array]
        loc_mark=[]
        nowcolor=0
        y_pos=max(y_array)
        key_list=y_pos.get_attr()
        y_pos=max([y_pos.get_by_attr(k) for k in key_list])
        y_pos=y_pos + 0.1
        for pair in self.outer_clu:
            color_array=[]
            color_array=pair[1]
            color_array.append(pair[0])
            #each segment
            if len(color_array)<2:
                continue
            for p in color_array:
                s1,e1=p
                #fill (s1,e1)
                loc_mark.append([(s1,y_pos),str(nowcolor)])
                for i in range(s1,e1):
                    clu_array[i]=nowcolor
            #for next time color changed
            nowcolor=nowcolor+1
        clu_array=[nowcolor*2 if x==max_clu else x for x in clu_array]
        outputname='rare_sequence_'
        outputname=outputname+self.name
        if draw==True and mark_outlier==True:
            draw_pic.draw_pic( y_array,clu_array,x_array,save_name=outputname,title=self.name,text_data=loc_mark,y_is_multi=True)
        pass
    pass

def show_rules_in_segment_mode(seg_dict,rule,rulenum,width=20):
    #seg array:
    #{name:y_array},...
    #one time one rule
    t_array_dict={}
    for name in seg_dict:
        temp_t_array=[0 for y in seg_dict[name]]
        t_array_dict[name]=temp_t_array
    #init all color finished
    start_array=rule[0][0]
    start_name={}
    end_array=rule[0][1]
    end_name={}
    believe=rule[1]
    loc_dict={}
    #in one key,
    rule_num=rulenum
    for k in start_array:
        loc_data=[]
        name=k[0]
        start_name[name]=1
        temp_color=[120 for i in t_array_dict[name]]
        y_pos=max(seg_dict[name])
        key_list=y_pos.get_attr()
        y_pos=max([y_pos.get_by_attr(k) for k in key_list])
        y_pos=y_pos+0.1
        for i in k[1:]:
            #i is x
            #y is seg_dict[name][x] +0.2
            #text is believe
            loc_data.append([(i,y_pos),str(believe)])
            
            for j in range(0,width):
                temp_color[min(i+j,len(temp_color)-1)]=int(believe)
        t_array_dict[name]=temp_color    
        loc_dict[name]=loc_data
    for k in end_array:
        loc_data=[]
        name=k[0]
        end_name[name]=1
        temp_color=[120 for i in t_array_dict[name]]
        y_pos=max(seg_dict[name])
        key_list=y_pos.get_attr()
        y_pos=max([y_pos.get_by_attr(k) for k in key_list])
        y_pos=y_pos+0.1
        for i in k[1:]:
            loc_data.append([(i,y_pos),str(believe)])
            for j in range(0,width):
                temp_color[min(i+j,len(temp_color)-1)]=int(believe)
        t_array_dict[name]=temp_color
        loc_dict[name]=loc_data
        
    
    
    for name in seg_dict:
        t_array=t_array_dict[name]
        y_array=seg_dict[name]
        x_array=[i for i in range(len(y_array))]
        outputname=name+'_rule_'+str(rule_num)
        outputname=outputname+'fre'+str(believe)[:5]
        temp_title=name
        if name in start_name:
            temp_title='start: '+name
        elif name in end_name:
            temp_title='end: '+ name
        if name in loc_dict:
            
            draw_pic.draw_pic( y_array,t_array,x_array,save_name=outputname,title=temp_title,text_data=loc_dict[name],y_is_multi=True)
        else:
            
            draw_pic.draw_pic( y_array,t_array,x_array,save_name=outputname,title=temp_title,y_is_multi=True)
        
        
    pass

def build_data_from_FPTree(FPTree=[],seq=[]):
    '''
    input:
        FPTree=[tree1,tree2,tree3,...]
        seq=[dataseq1(class segment_mode, it have dataseq),dataseq2,dataseq3,...]
    return:
        ret_value=[point of data association rule1, rule2,...]
        first,list all the effective rules[like node(clu1)=>node(clu2)] in a tree,
            then, for each rule, find the value the cluster stands for in segment_mode..
            next, link all the value by time order in one rule, as one data point
            push it in ret_value
    '''
    ret_value=[]
    for tre in FPTree:
        for r in tre.effective_rule:
            temp_list=[]
            for n in r[0]:
                #n[0][1:] is ok
                pos=n[0][1]
                temp_list=temp_list+tre.pos2value_dict[pos]
            ret_value.append(temp_list)
    return ret_value
    pass

if __name__=='__main__':
    
    
#    A=data_builder.data_builder(20,30,1200,0.025,1)
#    a_x_array=[x for x in range(1200)]
#    #draw_pic.draw_pic( b.randomlize_xlist,False,a)
#    
#    A.add_rare(100,80,[1,150])
#    A.add_rare(100,80,[300,450])
#    A.insert_rare_in_rlist()
#    A_seg=segment_mode(70,100, A.randomlize_xlist)
#    A_seg.slide_cos_search()
#    A_seg.density_clu()
#    A_sequence=A_seg.build_pattern_of_symbol('a')
#    
#    B=data_builder.data_builder(20,30,1200,0.025,1)
#    b_x_array=[x for x in range(1200)]
#    #draw_pic.draw_pic( b.randomlize_xlist,False,a)
#    
#    B.add_rare(100,80,[2,151])
#    B.add_rare(100,80,[301,451])
#    B.insert_rare_in_rlist()
#    B_seg=segment_mode(70,100, B.randomlize_xlist)
#    B_seg.slide_cos_search()
#    B_seg.density_clu()
#    B_sequence=B_seg.build_pattern_of_symbol('b')
    start=time.time()
    sitelist=[]
    for file in diskwalk("D:/zhp_workspace/35site").paths():
        print(start,file)
        filename=file
        sitelist.append(timeseq(filename))
    for site in sitelist:
        co_list=site.colist
        no2_list=site.no2list
        so2_list=site.so2list
        o3_list=site.o3list
        pm10_list=site.pm10list
        pm25_list=site.pm25list
        
        multi_dimen_seg=[]
        i=0
        for x in co_list:
            multi_dimen_seg.append(multi_dimen_data(
                    [co_list[i],no2_list[i],so2_list[i],o3_list[i],pm10_list[i],pm25_list[i]],
                    ['co',     'no2',      'so2',      'o3',      'pm10',      'pm25']))
            i=i+1
        
        co_seg=segment_mode(1,8, multi_dimen_seg,'co')
        
        #finding best dc
        co_seg.dc_factor=0.013
        step=0.001
        best_score=0
        best_dc=0
        best_co_seg=0
        '''for i in range(1):
            co_seg.slide_cos_search()
            co_seg.density_clu()
            score=len(co_seg.inner_clu)*co_seg.min_delta**2
            if score>best_score:
                best_score=score
                best_co_seg=co_seg
                best_dc=co_seg.dc_factor
            print ('min delta',co_seg.min_delta**2,'now score:',score)
            co_seg.dc_factor=co_seg.dc_factor+step
        '''    
        #co_seg=best_co_seg    
        #co_seg.dc_factor=best_dc
        co_seg.slide_cos_search(True)
        co_seg.density_clu(True)
        co_sequence=co_seg.build_pattern_of_symbol('co')
#        print (co_sequence)
    print (time.time(),'interval:',time.time()-start)
    
    
    ftree=FP_tree(0.01,0.3,2,8)
    ftree.add_sequence(co_sequence)
    ftree.structure_sub_tree()
    ftree.get_associate_rule()
    #print 2 pic
    i=0
    seg_dict={}
    seg_dict['co']=co_seg.data_sign

    for r in ftree.effective_rule:
        print (r[0][0],'=>',r[0][1],'lift:',r[1])
        show_rules_in_segment_mode(seg_dict,r,i)
        if i>10:
            break
        i=i+1
    rule_data=build_data_from_FPTree([ftree])
    pass
    '''
        no2_list=site.no2list
        no2_seg=segment_mode(70,100,no2_list,'no2')
        no2_seg.slide_cos_search()
        no2_seg.density_clu()
        no2_sequence=no2_seg.build_pattern_of_symbol('no2')
        
        so2_list=site.so2list
        so2_seg=segment_mode(70,100, so2_list,'so2')
        so2_seg.slide_cos_search()
        so2_seg.density_clu()
        so2_sequence=so2_seg.build_pattern_of_symbol('so2')
        
        o3_list=site.o3list
        o3_seg=segment_mode(70,100, o3_list,'o3')
        o3_seg.slide_cos_search()
        o3_seg.density_clu()
        o3_sequence=o3_seg.build_pattern_of_symbol('o3')
        
        pm10_list=site.pm10list
        pm10_seg=segment_mode(70,100, pm10_list,'pm10')
        pm10_seg.slide_cos_search()
        pm10_seg.density_clu()
        pm10_sequence=pm10_seg.build_pattern_of_symbol('pm10')
        
        pm25_list=site.pm25list
        pm25_seg=segment_mode(70,100, pm25_list,'pm25')
        pm25_seg.slide_cos_search()
        pm25_seg.density_clu()
        pm25_sequence=pm25_seg.build_pattern_of_symbol('pm25')
        
    
    
    
    
    
    
    
    
    ftree=FP_tree(2,0.6,4)
    ftree.add_sequence(co_sequence)
    ftree.add_sequence(no2_sequence)
    ftree.add_sequence(so2_sequence)
    ftree.add_sequence(o3_sequence)
    ftree.add_sequence(pm10_sequence)
    ftree.add_sequence(pm25_sequence)

    ftree.structure_sub_tree()
    ftree.get_associate_rule()
    #print 2 pic
    i=0
    seg_dict={}
    seg_dict['co']=co_seg.data_sign
    seg_dict['so2']=so2_seg.data_sign
    seg_dict['no2']=no2_seg.data_sign
    seg_dict['o3']=o3_seg.data_sign
    seg_dict['pm10']=pm10_seg.data_sign
    seg_dict['pm25']=pm25_seg.data_sign
    for r in ftree.effective_rule:
        print (r[0][0],'=>',r[0][1],'believe:',r[1])
        show_rules_in_segment_mode(seg_dict,r,i)
        if i>10:
            break
        i=i+1
    '''
#        
    #print (ret_val,'len:',len(ret_val))
    pass