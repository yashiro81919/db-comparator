#!/usr/bin/python
# Compared Result
class ObjectResultBean():
    def __init__(self):
        self.owner_name = None
        self.target_name = None
        self.status = None
        self.sr_list = []
        
class SourceResultBean():
    def __init__(self):
        self.owner_source = None
        self.target_source = None
        self.status = None
        self.line = None
        
class DatabaseResultBean():
    def __init__(self):
        self.owner = None
        self.target = None
        self.db_type = None
        self.tables = []
        self.views = []
        self.functions = []
        self.procedures = []
        self.triggers = []
        #Oracle specific
        self.sequences = []
        self.packages = []
        self.package_bodies = []
        self.materialized_views = []
           
        
