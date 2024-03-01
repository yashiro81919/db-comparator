#!/usr/bin/python
# Domain Object


class Database:
    def __init__(self):
        self.host_name = None
        self.db_name = None
        self.user_name = None
        self.password = None
        self.port = None
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


class DatabaseObject:
    def __init__(self):
        self.name = None
        self.source_list = []


class Table(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)
        self.temporary = None
        self.columns = []
        self.constraints = []
        self.indexes = []


class Column(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)
        self.table_name = None
        self.type = None
        self.data_length = None
        self.data_precision = None
        self.default_value = None
        self.nullable = None


class Constraint(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)
        self.table_name = None
        self.type = None
        self.columns = []
        self.reference_table_name = None
        self.reference_columns = []
        self.on_delete_type = None
        self.condition = None


class Index(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)
        self.table_name = None
        self.columns = []
        self.uniqueness = None
        self.index_type = None


class View(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)


class Procedure(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)


class Function(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)


class Trigger(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)

#Oracle specific
class MaterializedView(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)
        self.refresh_mode = None
        self.refresh_method = None
        self.indexes = []


class Package(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)


class PackageBody(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)


class Sequence(DatabaseObject):
    def __init__(self):
        DatabaseObject.__init__(self)






