# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 08:20:04 2019

@author: 赵怀菩
"""
from customize_tool import *
import draw_pic

import math
class AR_DPC(object):
    """
    first, make every element in rule became 1 dimen, like[1,2,3,4]
        not [[1,2],[3,4]]
    """
    def __init__(self,rules=[],name=''):
    
        self.rules=self.get_regular_rules([x[0] for x in rules])
        self.dc_factor=0.01
        self.sub_dict={}
        self.name=name
        #default dc set is 0.01 means 1%
        #self._build_dict_value2time(rules)
        pass
        
    def get_regular_rules(self,rules):
        ret_val=[]
        for r in rules:
            temp_r=[]
            for i in r:
                if type(i)==list or type(i)==tuple:
                    temp_r=temp_r+self.get_samplest_list(i)
                else:
                    temp_r.append(i)
            ret_val.append(temp_r)
        return ret_val
    
    def get_samplest_list(self,parent_list):
        ret_val=[]
        for i_or_list in parent_list:
            if type(i_or_list)==list or type(i_or_list)==tuple:
                #i_or_list is list
                ret_val=ret_val+self.get_samplest_list(i_or_list)
            else:
                #i_or_list is normal element
                ret_val.append(i_or_list)
        return ret_val
    def _build_dict_value2time(self,rules):
        self.value2time_dict={}
        #can't use it directly. for value has been diveide by self.rules.
        #time can only included in value.
    def cos_search(self,draw=False):
        self.sub_cos={}
        for rule1 in self.rules:
            for rule2 in self.rules:
                if rule1 != rule2:
                    #value=L2_distance(sub1,sub2)
                    value=new_cos(rule1,rule2)
                    self.__add_sub_value(tuple(rule1),tuple(rule2),value)
        dc=self.__count_dc_of_cos_dict()
        density_set=[]
        for rule1 in self.rules:
            seg1=tuple(rule1)
            neighborhood=0
            for rule2 in self.rules:
                seg2=tuple(rule2)
                value=self.__get_sub_value(seg1,seg2)
                if value!=0:
                    #0 is not exist
                    neighborhood=neighborhood+math.exp(-(value/dc)*(value/dc))
                    
            density_set.append([seg1,neighborhood])
#        for p1 in self.sub_dict:
#            seg1=self.sub_dict[p1]
#            
#            neighborhood=0
#            #neighborhood of s1,e1
#            for p2 in self.sub_dict:
#                seg2=self.sub_dict[p2]
#                value=self.__get_sub_value(seg1,seg2)
#                neighborhood=neighborhood+math.exp(-(value/dc)*(value/dc))
#                #gauess density
#                    #value is smaller, p is bigger . wanted
#            density_set.append([seg1,neighborhood])
        #density finish ,then sort
        density_set=sorted(density_set,key=lambda x:x[1])
        #print('density:',density_set)
        #x_array=[x[0][0] for x in density_set]
        #y_array=[x[1] for x in density_set]
        #t_array=[x for x in x_array]
        #all fin
        #print('theta')
        #draw_pic.draw_pic( y_array,t_array,x_array,False)
        
        
        self.data_rou_theta=[]
        i=0
        max_theta=0
        
        for pair in density_set:
            seg1=pair[0]
            neighborhood=pair[1]
            min_theta=999
            #in fact,theta means detla!!!
            if i+1<len(density_set):
                #forget to except the start place
                # it cannot repeat in same time
                for next_pair in density_set[i+1:]:
                    #compare with all rou> now
                    seg2=next_pair[0]
                    min_theta=min(min_theta,self.__get_sub_value(seg1,seg2))
                    pass
                max_theta=max(max_theta,min_theta)
                self.data_rou_theta.append([seg1,neighborhood,min_theta])
            else:
                self.data_rou_theta.append([seg1,neighborhood,max_theta])
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
        
        
        #t_array=[x[0][0] for x in self.data_rou_theta]
        t_array=[i for x in range(len(self.data_rou_theta))]
        for i in range(len(self.data_rou_theta)):
            rou=x_array[i]
            theta=y_array[i]
            gamma=rou*theta
            self.data_rou_theta[i]=[self.data_rou_theta[i][0],rou,theta,gamma]
        #all fin
        #print('x_array',x_array,'len',len(x_array))
        #print('x_array',y_array,'len',len(y_array))
        outputname='AR_DPC_rou_theta_'
        outputname=outputname+self.name
        if draw==True:
            draw_pic.draw_pic( y_array,t_array,x_array,False,save_name=outputname)
        pass
    
    def density_clu(self,draw=False,inner=6,outlier=1,mark_outlier=True):
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
#        if_partition={}
#        for key in self.sub_cos:
#            s1,e1=key
#            for i in range(s1,e1):    
#                if_partition[i]=False
        #max_e=len(if_partition)-1
        #record inner
        self.min_delta=999
        for pair in self.data_rou_theta:
            if pair[3]>=inner_clu_threshold:
                self.min_delta=min(pair[2],self.min_delta)
                seg1=pair[0]
                #match_data_sign=self.data_sign[s1:e1]
                s1e1_done=False
                now_center=(seg1)
                now_clu=[]
                #judge all have distance with center
                if self.sub_cos.get(seg1)==None:
                    seg1_dict={}
                else:
                    seg1_dict=self.sub_cos.get(seg1)
#                for i in range(s1,e1):   
#                    if i in if_partition and if_partition[i]==True:
#                        #has been divide
#                        s1e1_done=True
#                        break  
#                if s1e1_done==True:
##                    print (str(s1)+' used s1')
#                    continue
##                print (str(s1)+'-'+str(e1)+'un used s1')
                
                for key in seg1_dict:
                    seg2=key
#                    s2,e2=key
#                    if s2>e1 or s1>e2:
#                        s2e2_done=False
#                        
#                        for i in range(s2,e2):  
#                            if i in if_partition and if_partition[i]==True:
#                                #has been divide
#                                s2e2_done=True
#                                break
#                        if s2e2_done==True:
##                            print (str(s2)+' used s2')
#                            continue
##                        print (str(s1)+'-'+str(e1)+' and '+str(s2)+'-'+str(e2)+' can used')
                    if seg1_dict[key]<=self.dc:
                            #add to this clu
                        now_clu.append(key)
#                        for i in range(s2,e2):    
#                            if_partition[i]=True
#                            
#                        for i in range(s1,e1):    
#                            if_partition[i]=True
                    else:
#                            print (' not passed')
                        pass
                            #had been divided
                #often match at least appearence 2 times
                if len(now_clu)>1:
#                    clu_center.append([now_center,now_clu,match_data_sign])
                    clu_center.append([now_center,now_clu])
            else:
                pass
                #not in clu_center is outlier
        #outter can same with inner
#        for i in if_partition:
#            if_partition[i]=False
        
        if mark_outlier==True:
            #recode outer
            for pair in self.data_rou_theta:
                if pair[3]<outer_clu_threshold:
                    seg1=pair[0]
                    #match_data_sign=self.data_sign[s1:e1]
                    #s1e1_done=False
                    now_center=(seg1)
                    now_clu=[]
                    #judge all have distance with center
                    if self.sub_cos.get(seg1)==None:
                        seg1_dict={}
                    else:
                        seg1_dict=self.sub_cos.get(seg1)
#                    for i in range(s1,e1):   
#                        if i in if_partition and if_partition[i]==True:
#                            #has been divide
#                            s1e1_done=True
#                            break  
#                    if s1e1_done==True:
#                        continue
                    for key in seg1_dict:
                        seg2=key
#                        if s2>e1 or s1>e2:
#                            s2e2_done=False
#                            for i in range(s2,e2):   
#                                if i in if_partition and if_partition[i]==True:
#                                    #has been divide
#                                    s2e2_done=True
#                                    break
#                            if s2e2_done==True:
#                                continue
                        if seg1_dict[key]<=self.dc:
                            #add to this clu
                            now_clu.append(key)
#                                for i in range(s2,e2):    
#                                    if_partition[i]=True
#                                for i in range(s1,e1):    
#                                    if_partition[i]=True
#                                #had been divided
                    if len(now_clu)>1:
#                        out_center.append([now_center,now_clu,match_data_sign])
                        out_center.append([now_center,now_clu])
                else:
                    pass
            pass
        
        self.inner_clu=clu_center 
        self.outer_clu=out_center
        '''
        cannot show so far
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
        '''
        pass
    pass
    def build_pattern_of_symbol(self,unique_string):
        #unique string is important to differ this time sequence and other
        pattern_of_symbol=[]
        '''
        each index of pattern of symbol:
        ----in AR DPC, time is invisible, so it only have raw value and clustering center----
        ----pair[0]:raw value----
        ----pair[1]:clustering center----
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
            seg1=pair[0]
            all_start=[x[0] for x in pair[1]]
            key_array=[x[0] for x in pair[1]]
            key_array.insert(0,unique_string)
            hash_key=tuple(key_array)
            #all_start.append(s1)
            #all start position of this cluster
            
#            temp_list=[]
#            clu_center_in_dataseq=[]
#            temp_list=[self.data_sign_match_origin_dict[s1]]
#            if s1!=e1:
#                for i in range(s1+1,e1+1):
#                    temp_list.append(self.data_sign_match_origin_dict[i])
#            clu_center_in_dataseq.append(temp_list)
#            #we think s1,e1 is a continues time in data_sign, so will in dataseq, so we shouldn't separate
#            #the time. if it is [1,2,3], it will mean [1,2,3,4,5,6] there, not [[1,2],[3,4],[5,6]].
#            #each the element in pair[1] is like this.
#            point_data_sign_in_dataseq=[]
#            temp_list=[]
#            for s2,e2 in pair[1]:
#                temp_list=[self.data_sign_match_origin_dict[s1]]
#                if s2!=e2:
#                    for i in range(s2+1,e2+1):
#                        temp_list.append(self.data_sign_match_origin_dict[i])
#                point_data_sign_in_dataseq.append(temp_list)
            for start in all_start:
                if start not in start_record:
                    #pattern_of_symbol.append([start,hash_key,pair[2],clu_center_in_dataseq,point_data_sign_in_dataseq])
                    pattern_of_symbol.append([start,hash_key])
                    start_record.append(start)
            pass
        
        for pair in self.inner_clu:
            seg1=pair[0]
            all_start=[x[0] for x in pair[1]]
            key_array=[x[0] for x in pair[1]]
            key_array.insert(0,unique_string)
            hash_key=tuple(key_array)
            #all_start.append(s1)
            #all start position of this cluster
#            temp_list=[]
#            clu_center_in_dataseq=[]
#            temp_list=[self.data_sign_match_origin_dict[s1]]
#            if s1!=e1:
#                for i in range(s1+1,e1+1):
#                    temp_list.append(self.data_sign_match_origin_dict[i])
#            clu_center_in_dataseq.append(temp_list)
#            #we think s1,e1 is a continues time in data_sign, so will in dataseq, so we shouldn't separate
#            #the time. if it is [1,2,3], it will mean [1,2,3,4,5,6] there, not [[1,2],[3,4],[5,6]].
#            #each the element in pair[1] is like this.
#            point_data_sign_in_dataseq=[]
#            temp_list=[]
#            for s2,e2 in pair[1]:
#                temp_list=[self.data_sign_match_origin_dict[s1]]
#                if s2!=e2:
#                    for i in range(s2+1,e2+1):
#                        temp_list.append(self.data_sign_match_origin_dict[i])
#                point_data_sign_in_dataseq.append(temp_list)
            for start in all_start:    
                if start not in start_record:
#                    pattern_of_symbol.append([start,hash_key,pair[2],clu_center_in_dataseq,point_data_sign_in_dataseq])
                    pattern_of_symbol.append([start,hash_key])
                    start_record.append(start)
            
            pass
        pattern_of_symbol=sorted(pattern_of_symbol,key=lambda x:x[0])
        self.pattern_symbol=pattern_of_symbol
        
        return self.pattern_symbol
        pass
    def __add_sub_value(self,seg1,seg2,val):
        seg1_dict={}
        seg2_dict={}
        if self.sub_cos.get(seg1)==None:
            seg1_dict={}
        else:
            seg1_dict=self.sub_cos.get(seg1)
        if seg1_dict.get(seg2)==None:
            seg1_dict[seg2]=val
        else:
            pass
            #error. had been added
        self.sub_cos[seg1]=seg1_dict    
        
        if self.sub_cos.get(seg2)==None:
            seg2_dict={}
        else:
            seg2_dict=self.sub_cos.get(seg2)
        if seg2_dict.get(seg1)==None:
            seg2_dict[seg1]=val
        else:
            pass
            #error. had been added
        self.sub_cos[seg2]=seg2_dict   
        pass
    def __get_sub_value(self,seg1,seg2):
        s1,e1=seg1
        s2,e2=seg2
        seg1_dict={}
        
        if self.sub_cos.get(seg1)==None:
            #not exist
            #print (seg1,' not exist')
            return 0
        else:
            seg1_dict=self.sub_cos.get(seg1)
        if seg1_dict.get(seg2)==None:
            #not exist
            #print (seg2,' not exist')
            return 0
        else:
            return seg1_dict[seg2]
        pass
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
    #there is end of class
    pass

if __name__=='__main__':
    a=AR_DPC([[1,2,[3,[4]]],[[5,6],[7,[8,9]],10]])
    print (a.rules)