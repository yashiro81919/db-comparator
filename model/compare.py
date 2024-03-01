#!/usr/bin/python
# compare database objects
import result
import constant

def compare_source(owner_sources, target_sources):
    sr_list = []
    target_index = 0
    for source in owner_sources:
        #owner source is more then target source, put it's status to added.
        if target_index >= len(target_sources):
            add_source_result(sr_list, source, constant.STATUS_ADDED)
            continue
        if source.strip() == target_sources[target_index].strip():
            add_source_result(sr_list, source, constant.STATUS_NO_CHANGE)
            target_index += 1
        else:
            #use this list for saving column temporary.they may be marked deleted, or do nothing. 
            tmp_delete_list = []
            #only one line
            if len(target_sources) == 1:
                add_source_result(sr_list, source, constant.STATUS_ADDED)
            else:
                is_match = False
                for j in range(target_index + 1, len(target_sources)):
                    tmp_delete_list.append(target_sources[j - 1])
                    if source.strip() == target_sources[j].strip():
                        mark_deleted(sr_list, tmp_delete_list)
                        add_source_result(sr_list, source, constant.STATUS_NO_CHANGE) 
                        target_index = j + 1 
                        is_match = True
                        break
                if not is_match:
                   tmp_delete_list = []
                   add_source_result(sr_list, source, constant.STATUS_ADDED) 
    if target_index < len(target_sources):
        for i in range(target_index, len(target_sources)):
            add_source_result(sr_list, target_sources[i], constant.STATUS_DELETED) 
    return sr_list

def mark_deleted(sr_list, tmp_delete_list):
    for source in tmp_delete_list:
       add_source_result(sr_list, source, constant.STATUS_DELETED)
    tmp_delete_list = []   
                   
def add_source_result(sr_list, source, status):
    bean = result.SourceResultBean()
    if status == constant.STATUS_DELETED:
        bean.owner_source = ''
        bean.target_source = source
    elif status == constant.STATUS_ADDED:
        bean.owner_source = source
        bean.target_source = ''        
    elif status == constant.STATUS_NO_CHANGE:
        bean.owner_source = source
        bean.target_source = source
    bean.status = status
    bean.line = len(sr_list) + 1
    sr_list.append(bean) 
    
def compare_object(owner_objects, target_objects): 
    or_list = []
    owner_names = []
    target_names = []
    #get owner name list
    for obj in owner_objects:
       owner_names.append(obj.name)
    #get target name list
    for obj in target_objects:
       target_names.append(obj.name)
    #backup ownerNames
    name_baks = []
    name_baks.extend(owner_names)
    for obj in target_names:
        if owner_names.count(obj)  > 0:
            owner_names.remove(obj)
    #populate added object to ObjectResultBean
    for name in owner_names:
        bean = result.ObjectResultBean()
        bean.owner_name = name
        bean.target_name = ''
        owner = get_object_by_name(owner_objects, name)
        bean.status = constant.STATUS_ADDED
        bean.sr_list = compare_source(owner.source_list, [])
        or_list.append(bean)
    for obj in name_baks:
        if target_names.count(obj)  > 0:
            target_names.remove(obj)
    #populate removed object to ObjectResultBean
    for name in target_names:
        bean = result.ObjectResultBean()
        bean.owner_name = ''
        bean.target_name = name
        target = get_object_by_name(target_objects, name)
        bean.status = constant.STATUS_DELETED
        bean.sr_list = compare_source([], target.source_list)
        or_list.append(bean)
    for obj in owner_names:
        if name_baks.count(obj)  > 0:
            name_baks.remove(obj)
    #populate exists object to ObjectResultBean  
    for name in name_baks:
        bean = result.ObjectResultBean() 
        bean.owner_name = name
        bean.target_name = name 
        owner = get_object_by_name(owner_objects, name)
        target = get_object_by_name(target_objects, name)
        source_resources = compare_source(owner.source_list, target.source_list)
        bean.sr_list = source_resources
        bean.status = get_object_result_bean_status(source_resources) 
        or_list.append(bean)
    #order elements by name A-Z
    def sort_rule(e1, e2):
        name1 = None
        if e1.owner_name == None or e1.owner_name =='':
            name1 = e1.target_name
        else:
            name1 = e1.owner_name
        name2 = None
        if e2.owner_name == None or e2.owner_name =='':
            name2 = e2.target_name
        else:
            name2 = e2.owner_name
        return cmp(name1, name2)
    or_list.sort(sort_rule)
    return or_list           
                            
def get_object_by_name(objects, name):
    for obj in objects:
        if name == obj.name:
            return obj
    return None

def get_object_result_bean_status(source_result_beans):
    for bean in source_result_beans:
        if bean.status != constant.STATUS_NO_CHANGE:
            return constant.STATUS_UPDATED
    return constant.STATUS_NO_CHANGE

def split_source(full_source):
    return full_source.split('\n')
