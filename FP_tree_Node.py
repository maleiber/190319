# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 19:29:30 2018

@author: 赵怀菩
"""

class FT_tree_Node(object):
    def __init__(self,name,key,time,parent=None):
        self.name=name
        #name is belonging name of its tree
        self.key=key
        self.count=time
        self.parent=parent
        self.this_node_time=[]
        self.child={}
        pass
    def set_parent_time(self,parent):
        self.parent_node_time=parent
        pass
    def set_node_time(self,now):
        if type(now)==tuple:
            now=list(now)
        self.this_node_time=now
        pass
    def __del__(self):
        '''
        caution: when delete a node, remember to del all refereneces to this node, especially its parent's,which this func not mentioned
        use like this:
            now_node.child.pop(grand_child_key)
            del child_node
        '''
        self.parent=0
        for child_node_key in self.child:
            del self.child[child_node_key]
            self.child.pop(child_node_key)
        
    def show(self,index=1):
        print(' '*index,self.name,' ,[',self.this_node_time,'] len:',self.count)
        for child in self.child.values():
            child.show(index+1)
    
    #there is the pass of whole class FT TREE NODE
    pass
def get_node_leaf(ft_node,layer=1):
    ret_node=[]
    if len(ft_node.child)==0:
        if layer>2:
            ret_node.append(ft_node)
        return ret_node
    for key in ft_node.child:
        now_node=ft_node.child[key]
        ret_node=ret_node+get_node_leaf(now_node,layer+1)
    return ret_node
    pass
def get_node_full_name(ft_node):
    ret_val=[]
    p=ft_node
    while True:
        if p.parent==None:
            break
        else:
            ret_val.append(p.name)
            p=p.parent
    return ret_val
def get_key_array(ft_node):
    ret_val=[]
    p=ft_node
    while True:
        if p.parent==None or p.key=='root':
            break
        else:
            ret_val.insert(0,(p.key,p.count))
            p=p.parent
    return ret_val
def traverse_tree(root_node):
    ret_val=[]
    if root_node.parent==None:
        for child in root_node.child:
            first_child_node=root_node.child[child]
            for sec_child in first_child_node.child:
                now_node=first_child_node.child[sec_child]
                # qian xu
                ret_val.append(now_node)
                next_array=traverse_tree(now_node)
                ret_val=ret_val+next_array
    else:
        for child in root_node.child:
            now_node=root_node.child[child]
            #qian xu
            ret_val.append(now_node)
            next_array=traverse_tree(now_node)
            ret_val=ret_val+next_array
    return ret_val
    pass