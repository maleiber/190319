# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 09:26:14 2019

@author: 赵怀菩
"""
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import pandas as pd
import numpy as np
import time
import os
from sklearn import preprocessing
from operator import itemgetter, attrgetter
class timeseq(object):
    #timeseq is a seq of a site
    #therer might have numbers of time spice
    def __init__(self,filename):
        self.filename=filename
        self.colist=[]
        self.no2list=[]
        self.so2list=[]
        self.o3list=[]
        self.pm10list=[]
        self.pm25list=[]
        self.comiss=[]
        self.no2miss=[]
        self.so2miss=[]
        self.o3miss=[]
        self.pm10miss=[]
        self.pm25miss=[]
        self.datelist=[]
        self.__read__air()
        self.__read__date()
        self.__read__miss()
        self.__fill__miss()
        #[xxseq,timeseq,motifseq]
        self.co_seq=[]
        #[xxseq,length,time]
        self.co_match_frequency=[]
        self.no2_seq=[]
        self.so2_seq=[]
        self.o3_seq=[]
        self.pm10_seq=[]
        self.pm25_seq=[]
        #seq is a list of which each of element is a pair of [seq,time]
        #like [[seq1,time1],[seq2,time2],...]
        #self.drw_single_condition_with_single_site_plot(self.colist,self.datelist,'co',self.filename[-9:-4])
        self.__seprate__seq()
        self._build_motif_seq()
        #self._seq_match()
        #self._drw_match()
        #self.drw__seprate__seq()
        #self.drw_single_condition_with_single_site_plot(self.no2list,self.datelist,'no2',self.filename[-9:-4])
        #self.drw_single_condition_with_single_site_plot(self.so2list,self.datelist,'so2',self.filename[-9:-4])
        #self.drw_single_condition_with_single_site_plot(self.o3list,self.datelist,'o3',self.filename[-9:-4])
        #self.drw_single_condition_with_single_site_plot(self.pm10list,self.datelist,'pm10',self.filename[-9:-4])
        #self.drw_single_condition_with_single_site_plot(self.pm25list,self.datelist,'pm25',self.filename[-9:-4])
        
#        self.drw_multi_condition_with_single_site_plot(
#                [self.colist,self.no2list,self.so2list,self.o3list,self.pm10list,self.pm25list],
#                self.datelist,
#                ['co','no2','so2','o3','pm10','pm25'],self.filename[-9:-4])
    #under is take co as sample
    def _build_motif_seq(self):
        #motif take 15 flag now
        # in co:
        region=31
        comax=-999999
        comin=999999
        i=0
        #standardlize
        standard_seq=[]
        
        for seq in self.co_seq:
            
            standard_seq.extend(seq[0])
        standard_seq=preprocessing.scale(standard_seq)
        
        i=0    #indef of srandard_seq
        j=0    #index of self.co_seq
        for seq in self.co_seq:
            temp_seq=[]
            
            for seq_element in seq[0]:
                temp_seq.append(standard_seq[i])
                i=i+1
            self.co_seq[j][0]=temp_seq
            j=j+1
        i=0
        
        for seq in self.co_seq:
            temp_flag_seq=['undefined']
            prev=seq[0][0]
            for now in seq[0][1:]:
                detla=now-prev
                
                temp_flag_seq.append(detla)
                prev=now
                if detla>comax:
                    comax=detla
                if detla<comin:
                    comin=detla
            
            
            seq.append(temp_flag_seq)
            self.co_seq[i]=seq
            i=i+1
        
        region_array=np.arange(comin,comax+(comax-comin)/region,(comax-comin)/region)
        print (region_array)
        i=0
        for seq in self.co_seq:
            temp_flag_seq=seq[2]
            j=1
            for now in temp_flag_seq[1:]:
                temp_flag_seq[j]=self.__get_region_level(region_array,now)
                j=j+1
            self.co_seq[i][2]=temp_flag_seq
            #
            i=i+1
        
    def __get_region_level(self,region_array,value):
        level=0
        for lower_bound in region_array:
            if value<= lower_bound:
                return level
            level=level+1
        return level
    def _seq_match(self):
        minlength=13
        maxlength=25
        #of each seq, first index must be 'undefined', so add 1 from 6 to 7 & 24 to 25
        for seq in self.co_seq:
            motif_seq=seq[2]
            rlength=len(motif_seq)
            
            if rlength<minlength:
                #too small seq ,ignore
                continue
            nowlength=minlength
            
            while (not nowlength>maxlength) and nowlength<rlength:
                i=0
                while i+nowlength-1<rlength:
                    #l_seq
                    l_seq=motif_seq[i+1:i+nowlength]
                    
                    total=0
                    real_time_seq=[]
                    for r_seq in self.co_seq:
                        [time_seq,r_seq]=[r_seq[1],r_seq[2]]
                        #
                        #print (l_seq, r_seq)
                        pattern_array=''
                        #pattern_array=bm_test.BoyerMooreHorspool(l_seq, r_seq)
                        total=total+len(pattern_array)
                        
                        for m in pattern_array:
                            real_time_seq.append(time_seq[m])
                            
                        #time_seq[for index in pattern_array]
                    i=i+1
                    #print (l_seq,'appear time:',total)
                    if total>1:
                        self.co_match_frequency.append([l_seq,nowlength-1,total,np.var(l_seq),real_time_seq])
                nowlength=nowlength+1
            
        
    def _drw_match(self):
        print ('drw match')
        self.co_match_frequency=sorted(self.co_match_frequency, key=itemgetter(3,1,2),reverse=True)
        print (self.co_match_frequency)
        
        realx=[time.strftime('%Y%m%d %H',xx) for xx in self.datelist]
        
        xlist=pd.date_range(realx[0],realx[-1],freq='1H')
        
        fig,ax = plt.subplots()
        fig.set_size_inches(108.5, 10.5)
        
        xticks = pd.date_range(realx[0],realx[-1],freq='6H')
        xticklabels = xticks
        ax.plot(xlist,preprocessing.scale(self.colist)[:len(xlist)])
        #ax.plot(xlist,l)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels,rotation=75)
        ax.grid(True)
        
        
    #above is take co as sample
    def __seprate__seq(self):
        #do colist as a sample
        #fill the xx_seq
        tempseq=[]
        xxseq=[]
        timeseq=[]
        i=0
        misscount=0
        __seprate__max=4
        for dat in self.comiss:
            if dat==1:
                misscount+=1
                #fill average in nowseq
                if not(misscount>__seprate__max/2):
                    xxseq.append(self.colist[i])
                    timeseq.append(self.datelist[i])
                else:
                    if misscount==__seprate__max:
                       #do seprate the rest seq into a new seq
                       #let new became now
                       tempseq=[xxseq,timeseq]
                       self.co_seq.append(tempseq)
                       tempseq=[]
                       xxseq=[]
                       timeseq=[]
            else:
                if misscount>=__seprate__max:
                    #fill average in start
                    for j in range(int(__seprate__max/2)):
                        xxseq.append(self.colist[i+j-2])
                        timeseq.append(self.datelist[i+j-2])
                #fill the raw in nowseq
                xxseq.append(self.colist[i])
                timeseq.append(self.datelist[i])
                misscount=0
              
            i=i+1
        if len(xxseq)>0:
            tempseq=[xxseq,timeseq]
            self.co_seq.append(tempseq)
    
    def drw__seprate__seq(self):
        i=0
        for seq in self.co_seq:
            realx=[time.strftime('%Y%m%d %H',xx) for xx in seq[1]]
            xlist=pd.date_range(realx[0],realx[-1],freq='1H')
            
            fig,ax = plt.subplots()
            fig.set_size_inches(108.5, 10.5)
            
            xticks = pd.date_range(realx[0],realx[-1],freq='6H')
            xticklabels = xticks
            real_len=min(len(xlist),len(seq[0]))
            ax.plot(xlist[:real_len],seq[0][:real_len])
            #ax.plot(xlist,l)
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels,rotation=75)
            ax.grid(True)
            
            airname='co'
            sitename='id3'
            outputname='seprate_seq_['+airname+'-'+sitename+']_seqno_'+str(i)
            outputname=outputname+'.png'
            plt.savefig(outputname, dpi=100)
            
            plt.show()
            i+=1
            
    def __read__air(self):
        with open(self.filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['co']!='NULL':
                    self.colist.append(float(row['co']))
                else:
                    self.colist.append(float(0))
                if row['no2']!='NULL':
                    self.no2list.append(float(row['no2']))
                else:
                    self.no2list.append(float(0))
                if row['so2']!='NULL':
                    self.so2list.append(float(row['so2']))
                else:
                    self.so2list.append(float(0))
                if row['o3']!='NULL':
                    self.o3list.append(float(row['o3']))
                else:
                    self.o3list.append(float(0))
                if row['pm10']!='NULL':
                    self.pm10list.append(float(row['pm10']))
                else:
                    self.pm10list.append(float(0))
                if row['pm25']!='NULL':
                    self.pm25list.append(float(row['pm25']))
                else:
                    self.pm25list.append(float(0))
        f.close()
        
    def __read__date(self):
        with open(self.filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                temptime=time.strptime(row['date']+' '+str(int(row['hour']))+':00:00',"%Y/%m/%d %H:%M:%S")
                self.datelist.append(temptime)
        f.close()
    
    def __read__miss(self):
        with open(self.filename) as f:
            reader = csv.DictReader(f)
            comiss=[]
            no2miss=[]
            so2miss=[]
            o3miss=[]
            pm10miss=[]
            pm25miss=[]
            for row in reader:
                tempstr=row['miss_data']
                if 'co' in tempstr or row['co']=='NULL':
                    comiss.append(1)
                else:
                    comiss.append(0)
                if 'no2' in tempstr or row['no2']=='NULL':
                    no2miss.append(1)
                else:
                    no2miss.append(0)
                if 'so2' in tempstr or row['so2']=='NULL':
                    so2miss.append(1)
                else:
                    so2miss.append(0)
                if 'o3' in tempstr or row['o3']=='NULL':
                    o3miss.append(1)
                else:
                    o3miss.append(0)
                if 'pm10' in tempstr or row['pm10']=='NULL':
                    pm10miss.append(1)
                else:
                    pm10miss.append(0)
                if 'pm25' in tempstr or row['pm25']=='NULL':
                    pm25miss.append(1)
                else:
                    pm25miss.append(0)
            
            self.comiss=comiss
            self.no2miss=no2miss
            self.so2miss=so2miss
            self.o3miss=o3miss
            self.pm10miss=pm10miss
            self.pm25miss=pm25miss
        f.close()
    
    def __fill__miss(self):
        newdate=[]
        [self.colist,newdate]=fillmiss(self.colist,self.comiss,self.datelist)
        
        [self.no2list,newdate]=fillmiss(self.no2list,self.no2miss,self.datelist)
        
        [self.so2list,newdate]=fillmiss(self.so2list,self.so2miss,self.datelist)
        
        [self.o3list,newdate]=fillmiss(self.o3list,self.o3miss,self.datelist)
        
        [self.pm25list,newdate]=fillmiss(self.pm25list,self.pm25miss,self.datelist)
        
        [self.pm10list,newdate]=fillmiss(self.pm10list,self.pm10miss,self.datelist)
        self.datelist=newdate
    
    def drw_single_condition_with_single_site_plot(self,l,xaxis,airname,sitename):
        #min_max_scaler = preprocessing.MinMaxScaler()
        y_array=preprocessing.scale(l)[:len(xlist)]
        x_array=[i for i in range(len(y_array))]
        
        
        
        
        
        
        
#        realx=[time.strftime('%Y%m%d %H',xx) for xx in xaxis]
#        
#        xlist=pd.date_range(realx[0],realx[-1],freq='1H')
#        
#        fig,ax = plt.subplots()
#        fig.set_size_inches(108.5, 10.5)
#        
#        xticks = pd.date_range(realx[0],realx[-1],freq='6H')
#        xticklabels = xticks
#        ax.plot(xlist,preprocessing.scale(l)[:len(xlist)])
#        #ax.plot(xlist,l)
#        ax.set_xticks(xticks)
#        ax.set_xticklabels(xticklabels,rotation=75)
#        ax.grid(True)
#        
        #ax1=fig.add_subplot(1,1,1)
        #ax1.plot(realx,preprocessing.scale(l),linewidth=0.5)
        
        #aa=pd.date_range(realx[0],realx[-1],freq='6H')
        #print (realx)
        #ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))    
        #plt.xticks(aa,rotation=90)#时间间隔
        #ax1.set_xlabel('Time',fontsize=30)
        #plt.xticks(rotation=90)
        
        #legend1.get_frame().set_facecolor('#FFFFFF')
        #ax1.plot(realx,color='#4A7EBB',linewidth=4)
        outputname='single_condition_with_single_site__['+airname+'-'+sitename+']'
        outputname=outputname+'.png'
        
#        plt.savefig(outputname, dpi=100)
        plt.show()

    def drw_multi_condition_with_single_site_plot(self,l,xaxis,airname,sitename):
        realx=[time.strftime('%Y%m%d %H',xx) for xx in xaxis]
        
        xlist=pd.date_range(realx[0],realx[-1],freq='1H')
        
        fig,ax = plt.subplots()
        fig.set_size_inches(108.5, 10.5)
        
        xticks = pd.date_range(realx[0],realx[-1],freq='6H')
        xticklabels = xticks
        for element in l:
            ax.plot(xlist,preprocessing.scale(element)[:len(xlist)],linewidth=0.5)
            #ax.plot(xlist,l)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels,rotation=75)
        ax.grid(True)
       
        outputname='multi_condition_with_single_site__['
        for air in airname:
            outputname=outputname+air
        outputname=outputname+'-'+sitename+']'
        outputname=outputname+'.png'
        
        plt.savefig(outputname, dpi=100)
        plt.show()

def fillmiss(raw_list,miss_data,datelist):
    #fillmiss with nearest 8 sample's average
    raw_list1=[]
    #print(len(miss_data),len(raw_list))
    for i in raw_list:
        raw_list1.append(float(i)/8)
    prev=datelist[0]
    datelist1=[tempdate for tempdate in datelist]
    prev=datelist1[0]
    i=0
    for dat in datelist1[1:]:
        sec=int(time.mktime(dat)-time.mktime(prev))
        while sec>3600:
            sec-=3600
            temptime=time.localtime(int(time.mktime(prev))+3600)
            #temptime new time!
            datelist1.insert(i,temptime)
            raw_list1.insert(i,0)
            raw_list.insert(i,0)
            miss_data.insert(i,1)
            prev=temptime
            i=i+1
        prev=dat    
        i=i+1
    
    leng=len(raw_list1)
    step1=[]
    step2=[]
    step3=[]
    i=0
    while i<len(raw_list1):
        k=0
        while i+k<leng and miss_data[i+k]!=0:
            k=k+1
        if(i+k>=leng):
            l=raw_list1[i-1]
        else:
            l=raw_list1[i+k]
        k=k+1
        while i+k<leng and miss_data[i+k]!=0:
            k=k+1
        if(i+k>=leng):
            r=l
        else:
            r=raw_list1[i+k]
        step1.append(l+r)
        i=i+1
    
    i=0
    leng=len(step1)
    while i<len(step1):
        k=2
        if(i+k>=leng):
            l=step1[i-1]
        else:
            l=step1[i]
        k=k+1
        if(i+k>=leng):
            r=l
        else:
            r=step1[i+2]
        step2.append(l+r)
        i=i+1
    
    i=0
    leng=len(step2)
    while i<len(step2):
        k=4
        if(i+k>=leng):
            l=step2[i-1]
        else:
            l=step2[i]
        k=k+1
        if(i+k>=leng):
            r=l
        else:
            r=step2[i+4]
        step3.append(l+r)
        i=i+1
    ret_val=[[],[]]
    i=0
    for if_miss in miss_data:
        if if_miss==1:
            ret_val[0].append(step3[i])
        else:
            ret_val[0].append(raw_list[i])
        i=i+1
    ret_val[1]=datelist1
    return ret_val

##diskwalk is a class used to find source files in a directory.
class diskwalk(object):
        def __init__(self,path):
                self.path = path
        def paths(self):
                path=self.path
                path_collection=[]
                for dirpath,dirnames,filenames in os.walk(path):
                        for file in filenames:
                                fullpath=os.path.join(dirpath,file)
                                path_collection.append(fullpath)
                return path_collection

if __name__=='__main__':
    sitelist=[]
    for file in diskwalk("D:/zhp_workspace/35site").paths():
        print(file)
        filename=file
        sitelist.append(timeseq(filename))
        
        