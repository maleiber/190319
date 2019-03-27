# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 15:28:19 2018

@author: 赵怀菩
"""
from FP_tree_Node import *

class FP_tree(object):
    #optimized for timing sequence
    def __init__(self,support=0.1,in_built_confidence=0.3,lift=1,window_width=12,max_depth=10):
        self.support=support
        #support is min time a signnal appear.
        #    if less than it, the node will be prune after builing a tree
        self.lift=lift
        self.build_confidence=in_built_confidence
        self.window=window_width
        self.max_depth=max_depth
        #believe is lift
        self.time_seq_data=[]
        self.sum_seq_num=0
        self.y_array={}
        self.sub_tree=[]
        self.key2pos_dict={}
        #    key  ,  all position
        self.count_dict={}
        #    key  ,  count
        self.pos2key_dict={}
        #    name , key
        self.pos2value_dict={}
        pass
    def add_y_array(self,name,y_array):
        self.y_array[name]=y_array
    
    
    def add_sequence(self,raw_seq):
        '''
        raw_seq must like:
        #    [ [time1,(name1,signal1),...],[time2,(name2,signal2),...],....]
            the element after pair[1] will not used.
        #signal must be unique!!
        #need to build a FPTree for a time line
        # one time, one sequence
#        seq_dict={}
#        tree_name=raw_seq[0][1][0]
        '''
#        
        self.time_seq_data.append(raw_seq)
        self.cal_seq_num()
        pass
    def cal_seq_num(self):
        for x in self.time_seq_data:
            self.sum_seq_num=self.sum_seq_num+len(x)
        pass
    
    def init_sub_tree(self):
        
        #first child
        for raw_x_seq in self.time_seq_data:
            name=raw_x_seq[0][1][0]
            now_parent=FT_tree_Node(name,'root',0)
            seq_dict={}
            node_inf=[]
            
            #count time
            for pair in raw_x_seq:
                
                all_position=pair[1][1:]
                self.key2pos_dict[pair[1]]=all_position
                #but there are only start time point
                for pos in all_position:
                    if self.pos2value_dict.get(pos)==None:
                        self.pos2value_dict[pos]=pair[2]
                    if self.pos2key_dict.get(pos)==None:
                        now_key=[]
                    else:
                        now_key=self.pos2key_dict.get(pos)
                    if [name,pair[1]] not in now_key:
                        now_key.append([name,pair[1]])
                    #    name , key
                    self.pos2key_dict[pos]=now_key
                    
                if pair[1] in self.count_dict:
                    seq_dict[pair[1]]=seq_dict[pair[1]]+1
                else:
                    seq_dict[pair[1]]=1
                    #count key
                    
                    #node_inf=sorted(node_inf,key=lambda x:x[0],reverse=True)
                self.count_dict.update(seq_dict)
            #node_inf=[(seq_dict[key],key) for key in seq_dict if seq_dict[key]>=self.support]
            node_inf=[(seq_dict[key],key) for key in seq_dict if seq_dict[key]>=1]
            for node_val in node_inf:
                now_node=FT_tree_Node(name,node_val[1],node_val[0],now_parent)
                all_position=node_val[1][1:]
                now_node.set_node_time(all_position)
                now_parent.child[node_val[1]]=now_node
                    
            self.sub_tree.append(now_parent)
        
        #second child
        for now_parent_node in self.sub_tree:        
            for child_key in now_parent_node.child:
                now_node=now_parent_node.child[child_key]
                now_origin_time=now_node.this_node_time
                #(1,3,5,7)
                # time is position array key appear
                accept_pos={}
                #form accept time
                for start in now_origin_time:
                    for i in range(0,1+self.window):
                        accept_pos[start+i]=1
                accept_pos=[pos for pos in accept_pos]
                #(2,3,4,5,6,7)
                #searching alivable key by accept pos
                key_set={}
                for pos in accept_pos:
                    if self.pos2key_dict.get(pos)==None:
                        continue
                    else:
                        temp_set=self.pos2key_dict[pos]
                        for pair in temp_set:
                            key_set[pair[1]]=pair[0]
                            #key[position] = belonging tree
                #chose the key-char not in this tree and reach the support requirement
                #do not let next key and nowkey same
                accept_key=[key for key in key_set if list(key[1:])!=now_node.this_node_time
                                and self.count_dict[key]>=1
                            ]
                #accept_key=[key for key in key_set if self.count_dict[key]>=self.support
                #            ]
                #now can use acckey to make new node
                for alivable_key in accept_key:
                    #c1,b1
                    #take origin time of c1
                    y_position=alivable_key[1:]
                    #take intersection y and accept pos as new node's time
                    intersection=[x for x in y_position if x in accept_pos]
                    
                    #support condition
                    #support is a ratio
                    if len(intersection)/self.sum_seq_num<self.support:
                        #invalid intersection
                        pass
                    elif len(intersection)/len(now_origin_time)<self.build_confidence:
                        #invalid intersection
                        pass
                    elif now_node.child.get(alivable_key)==None:
                        # new node
                        new_name=alivable_key[0]
                        new_node=FT_tree_Node(new_name,alivable_key,len(intersection),now_node)
                        #take node time information
                        new_node.set_node_time(intersection)
                        new_node.set_parent_time(now_origin_time)
                        #add child
                        now_node.child[alivable_key]=new_node
                        pass
                    else:
                        #error
                        #because accept_key is from key in dict. cant be multiple
                        pass
        
        pass
        
    def expand_sub_tree(self):
        '''
        temporary deprecated. use init sub tree only
        '''
        #expand tree by other tree
        #avoid repeat parent
        #return if add new node this traverse
        if_new=False
        
        #end of fromer and start of latter should be same
        # partly like init ofsecond child
        #X for each tree
        for now_parent_node in self.sub_tree:        
            x_list=get_node_leaf(now_parent_node)
            #for x_node in x_list
            for leaf_node in x_list:
                now_node=leaf_node
                now_origin_time=now_node.this_node_time
                #(1,3,5,7)
                # time is position array key appear
                accept_pos={}
                #form accept time
                for start in now_origin_time:
                    for i in range(1,1+self.window):
                        accept_pos[start+i]=1
                accept_pos=[pos for pos in accept_pos]
                #(2,3,4,5,6,7)
                #searching alivable key by accept pos
                key_set={}
                for pos in accept_pos:
                    if self.pos2key_dict.get(pos)==None:
                        #position exceed 
                        pass
                    else:
                        temp_set=self.pos2key_dict[pos]
                        for pair in temp_set:
                            key_set[pair[1]]=pair[0]
                            #key = belonging tree
                
                #chose the key-char not in this tree and reach the support requirement
                #x_full_name=get_full_name(x_node)
                
                
                x_full_name=get_node_full_name(now_node)
                
                #have problem
                accept_key=[key for key in key_set if key_set[key] not in x_full_name
                                and self.count_dict[key]>=self.support
                            ]
                
                #now can use acckey to make new node
                for alivable_key in accept_key:
                    #c1,b1
                    #take origin time of c1
                    y_position=alivable_key[1:]
                    #take intersection y and accept pos as new node's time
                    intersection=[x for x in y_position if x in accept_pos]
                    
                    if len(intersection)/self.sum_seq_num<self.support:
                        #invalid intersection
                        pass
                    elif len(intersection)/len(now_origin_time)<self.build_confidence:
                        #invalid intersection
                        pass
                    elif now_node.child.get(alivable_key)==None:
                        if_new=True
                        # new node
                        new_name=alivable_key[0]
                        new_node=FT_tree_Node(new_name,alivable_key,len(intersection),now_node)
                        #take node time information
                        new_node.set_node_time(intersection)
                        new_node.set_parent_time(now_origin_time)
                        #add child
                        now_node.child[alivable_key]=new_node
                        pass
                    else:
                        #error
                        #because accept_key is from key in dict. cant be multiple
                        pass
        
        #prune branch by  appearence, 
        return if_new
        pass
    
    def structure_sub_tree(self):
        self.init_sub_tree()
        i=0
        while self.expand_sub_tree()==True and i<self.max_depth:
            i=i+1
#            for now_parent_node in self.sub_tree:  
#                now_parent_node.show()
#                pass
            pass

        print ('finished struct')
        for now_parent_node in self.sub_tree:  
            now_parent_node.show()
        pass

        
    def show_tree(self):
        for now_parent_node in self.sub_tree:  
            now_parent_node.show()
        pass
    def get_associate_rule(self):
        self.rule_dict={}
        for sub_tree in self.sub_tree:
            for now_node in traverse_tree(sub_tree):    
                #now node as end
                key_array=get_key_array(now_node)
                #[0] is key, [1] is count
                temp_key_array=[x[0] for x in key_array]
                count_array=[x[1] for x in key_array]
                end_support=count_array.pop()
                end_key_array=[temp_key_array.pop()]
                #temp key array only contain key
                while len(temp_key_array)>0:
                    start_key_array=temp_key_array
                    start_support=count_array.pop()
                    lift=end_support/start_support
                    lift=lift*self.sum_seq_num/len(self.key2pos_dict[end_key_array[0]])
                    #len(self.key2pos_dict[end_key_array[0]]) is end key appear time
                    s_tuple=tuple(start_key_array)
                    e_tuple=tuple(end_key_array)
                    self.rule_dict[s_tuple,e_tuple]=lift
                    
                    convert_key=temp_key_array.pop()
                    end_key_array.append(convert_key)
                #[0] is key, [1],is count
        
        #get rules finished
        self.rule_list=[]
        for k in self.rule_dict:
            self.rule_list.append((k,self.rule_dict[k]))
        self.rule_list=sorted(self.rule_list,key=lambda x:x[1],reverse=True)
        
        self.effective_rule=[i for i in self.rule_list if i[1]>=self.lift]
        print ('all rule size:',len(self.rule_dict))
        
        for k in self.rule_dict:
            print (k[0],'=>',k[1],'lift:',self.rule_dict[k])
        print ('efective rule size:',len(self.effective_rule))
        for r in self.effective_rule:
            #in r,
            #r[0][0]left key, r[0][1] is right key
            #r[0][][0][0]is mark, r[0][][0][1:] is time
            #r[1] is lift
            
            print (r[0][0],'=>',r[0][1],'lift:',r[1])
#        pass
    
    def trim_tree(self,goal_support=0.1,goal_confidence=0.3,goal_lift=1,max_depth=10):
        node_list=[]
        #a queue
        for now_parent_node in self.sub_tree:
            node_list.append((now_parent_node,0))
        
        while len(node_list)!=0:
            now_parent_node,deep=node_list.pop(0)
            #first trim
            for child_key in list(now_parent_node.child.keys()):
                now_node=now_parent_node.child[child_key]
                #next time, now_node as parent node
                #now_node.this_node_time
                trim=False
                for grand_child_key in list(now_node.child.keys()):
                    child_node=now_node.child[grand_child_key]
                    #child_node.this_node_time
                    if child_node.count/self.sum_seq_num<self.support:
                        trim=True
                    elif child_node.count/now_node.count<self.build_confidence:
                        trim=True
                    elif deep+1>=max_depth:
                        trim=True
                    else:
                        start_support=now_node.count
                        end_support=child_node.count
                        lift=end_support/start_support
                        lift=lift*self.sum_seq_num/len(self.key2pos_dict[child_node.key])
                        #len(self.key2pos_dict[end_key_array[0]]) is end key appear time
                        #compare the lift
                        if lift < goal_lift:
                            trim=True
                    if trim== True:
                        #node.child[grand_child_key]=child_node
                        #it is unique references
                        now_node.child.pop(grand_child_key)
                        del child_node
                #then add now_node to list if it have grandchild can trim
                if len(now_node.child)>0 and deep<max_depth:
                    node_list.append((now_node,deep+1))
            
                
        pass
    
    #the pass of class FPTree
    pass


if __name__=='__main__':
    a=[]
    b=[]
    c=[]
    a1=('a',1,5,9,13,16)
    a2=('a',2,5,6)
    a3=('a',6,10)
    '''b1=('b',2,8)
    b2=('b',6,10)
    c1=('c',3,9)
    c2=('c',7,11)
    d1=('d',1,4,8,10,12)
    '''
    a=[[1,a1],[2,a2],[5,a1],[5,a2],[6,a2],[6,a3],[9,a1],[10,a3],[13,a1],[16,a1]]
    '''b=[[2,b1],[6,b2],[8,b1],[10,b2]]
    c=[[3,c1],[7,c2],[9,c1],[11,c2]]
    d=[[1,d1],[4,d1],[8,d1],[10,d1],[12,d1]]
    '''
    ftree=FP_tree(0.1,0.3,2,1)
    ftree.add_sequence(a)
    #ftree.add_sequence(b)
    #ftree.add_sequence(c)
    #ftree.add_sequence(d)
    ftree.structure_sub_tree()
    ftree.get_associate_rule()
    #ftree.trim_tree(0.1,0.3,2,2)
    #ftree.show_tree()
    #ftree.get_associate_rule()
#    for sub_tree in ftree.sub_tree:
#        for node in traverse_tree(sub_tree):    
#            print (node.key,'time:',node.this_node_time,',key ',get_key_array(node))
    pass