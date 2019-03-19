# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 08:19:16 2018

@author: 赵怀菩
"""
import os
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