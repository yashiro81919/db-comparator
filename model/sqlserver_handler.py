#!/usr/bin/python
# SqlServer handler
import _mssql
import bean
import compare

SQL_GET_TABLES = '''
select upper(t.TABLE_NAME) TABLE_NAME,upper(c.COLUMN_NAME) COLUMN_NAME,c.COLUMN_DEFAULT,
substring(c.IS_NULLABLE,1,1) NULLABLE,c.DATA_TYPE,c.CHARACTER_MAXIMUM_LENGTH DATA_LENGTH,
c.NUMERIC_PRECISION DATA_PRECISION, c.NUMERIC_SCALE DATA_SCALE,
IS_IDENTITY=case when i.column_name is null then 0 else 1 end
from information_schema.columns c inner join information_schema.tables t
on c.table_name=t.table_name and t.table_type='BASE TABLE'
left join (select s_t.name TABLE_NAME, s_ic.name COLUMN_NAME from sys.identity_columns s_ic, sys.tables s_t where s_ic.object_id=s_t.object_id) i
on (t.table_name=i.table_name and c.column_name=i.column_name)
order by t.table_name, c.ordinal_position'''

SQL_GET_INDEXES = '''
select upper(t.name) TABLE_NAME, upper(i.name) INDEX_NAME, upper(c.name) COLUMN_NAME,
i.IS_UNIQUE UNIQUENESS, i.IS_PRIMARY_KEY, i.TYPE_DESC INDEX_TYPE
from sys.index_columns ic, sys.tables t, sys.indexes i, sys.columns c
where i.object_id=t.object_id
and ic.object_id=i.object_id
and ic.index_id=i.index_id
and ic.object_id=c.object_id
and ic.column_id=c.column_id
and i.IS_PRIMARY_KEY=0 and i.is_unique_constraint=0
order by t.name,i.index_id, ic.key_ordinal'''

SQL_GET_PKS = '''
select upper(t.name) TABLE_NAME, upper(i.name) CONSTRAINT_NAME, upper(c.name) COLUMN_NAME,
i.IS_UNIQUE UNIQUENESS, i.IS_PRIMARY_KEY, i.TYPE_DESC INDEX_TYPE
from sys.index_columns ic, sys.tables t, sys.indexes i, sys.columns c
where i.object_id=t.object_id
and ic.object_id=i.object_id
and ic.index_id=i.index_id
and ic.object_id=c.object_id
and ic.column_id=c.column_id
and i.IS_PRIMARY_KEY=1
order by t.name,i.index_id, ic.key_ordinal'''

SQL_GET_UKS = '''
select upper(t.name) TABLE_NAME, upper(i.name) CONSTRAINT_NAME, upper(c.name) COLUMN_NAME,
i.IS_UNIQUE UNIQUENESS, i.IS_PRIMARY_KEY, i.TYPE_DESC INDEX_TYPE
from sys.index_columns ic, sys.tables t, sys.indexes i, sys.columns c
where i.object_id=t.object_id
and ic.object_id=i.object_id
and ic.index_id=i.index_id
and ic.object_id=c.object_id
and ic.column_id=c.column_id
and i.is_unique_constraint=1
order by t.name,i.index_id, ic.key_ordinal'''

SQL_GET_FKS = '''
select upper(fk.name) CONSTRAINT_NAME, upper(t.name) TABLE_NAME, upper(c.name) COLUMN_NAME,
upper(rt.name) R_TABLE_NAME, upper(rc.name) R_COLUMN_NAME,
DELETE_RULE=case delete_referential_action when 0 then 'NO ACTION' else 'CASCADE' end,
update_referential_action_desc UPDATE_RULE
from sys.foreign_key_columns fkc, sys.foreign_keys fk, sys.tables t, sys.columns c, sys.tables rt, sys.columns rc
where fkc.constraint_object_id=fk.object_id
and fk.parent_object_id=t.object_id
and fkc.parent_object_id=c.object_id
and fkc.constraint_column_id=c.column_id
and fkc.referenced_object_id=rt.object_id and fkc.referenced_column_id=rc.column_id and fkc.referenced_object_id=rc.object_id
order by t.name, fk.name'''

SQL_GET_CHECKS = '''
select upper(t.name) TABLE_NAME, upper(cc.name) CONSTRAINT_NAME,
upper(c.name) COLUMN_NAME, CAST(cc.DEFINITION AS TEXT) SEARCH_CONDITION
from sys.check_constraints cc, sys.tables t, sys.columns c
where cc.parent_column_id=c.column_id
and cc.parent_object_id=t.object_id
and c.object_id=t.object_id'''

SQL_GET_FUNCTIONS = '''
select upper(o.NAME) NAME, CAST(sm.definition AS TEXT) TEXT
from  sys.sql_modules sm, sys.objects o
where sm.object_id=o.object_id and o.type='FN'
order by o.name'''

SQL_GET_PROCEDURES = '''
select upper(o.NAME) NAME, CAST(sm.definition AS TEXT) TEXT
from  sys.sql_modules sm, sys.procedures o
where sm.object_id=o.object_id and is_ms_shipped=0
order by o.name'''

SQL_GET_TRIGGERS = '''
select upper(t.name) TABLE_NAME, upper(o.NAME) NAME, CAST(sm.definition AS TEXT) TEXT
from  sys.sql_modules sm, sys.triggers o, sys.tables t
where sm.object_id=o.object_id and o.is_ms_shipped=0
and o.parent_id=t.object_id
order by o.name'''

SQL_GET_VIEWS = '''
select upper(o.NAME) VIEW_NAME, CAST(sm.definition AS TEXT) TEXT
from  sys.sql_modules sm, sys.views o
where sm.object_id=o.object_id and o.is_ms_shipped=0
order by o.name'''

#define the maxium length for text
MAX_TEXT_SIZE = 'SET TEXTSIZE 1024000'

def get_database(host_name, db_name, user_name, password, port):
    db = None
    try:
        #TODO some bugs in sqlserver driver, so port is useless at present
        db = _mssql.connect(server=host_name, user=user_name, password=password, database=db_name)
        db.execute_non_query(MAX_TEXT_SIZE)
        
        database = bean.Database()
        database.host_name = host_name
        database.db_name = db_name
        database.user_name = user_name
        database.password = password
        database.port = port
        database.tables = _get_tables(db)
        database.views = _get_views(db)
        database.functions = _get_functions(db)
        database.procedures = _get_procedures(db)
        database.triggers = _get_triggers(db)
    except:
        raise
    finally:
        if db != None:
            db.close()
    return database

def _get_tables(db):
    l = []
    results = _query(db, SQL_GET_TABLES)
    indexes = _get_indexes(db)
    constraints = []
    constraints.extend(_get_pks(db))
    constraints.extend(_get_uks(db))
    constraints.extend(_get_fks(db))
    constraints.extend(_get_checks(db))
    
    table_dict = {}
    for row in results:
        table_name = row['TABLE_NAME']
        table = table_dict.get(table_name)
        if table == None:
            table = bean.Table()
            table.name = table_name
            table_dict[table_name] = table
        column = bean.Column()
        column.table_name = table_name
        column.name = row['COLUMN_NAME']
        column.default_value = row['COLUMN_DEFAULT']
        column.nullable = row['NULLABLE']
        column.type = row['DATA_TYPE']
        column.data_length = row['DATA_LENGTH']
        column.data_precision = row['DATA_PRECISION']
        table.columns.append(column)
    #set index
    for index in indexes:
        table_dict.get(index.table_name).indexes.append(index)
    #set constraints
    for constraint in constraints:
        table_dict.get(constraint.table_name).constraints.append(constraint)  
    for table in table_dict.values():
        table.source_list = _get_table_ddl(table)
        l.append(table)
    return l

def _get_views(db):
    l = []
    results = _query(db, SQL_GET_VIEWS)
    for row in results:
        name = row['VIEW_NAME']
        text = row['TEXT']
        view = bean.View()
        view.name = name
        view.source_list.extend(compare.split_source(text))
        l.append(view)
    return l

def _get_functions(db):
    l = []
    results = _query(db, SQL_GET_FUNCTIONS)
    function_dict = {}
    for row in results:
        name = row['NAME']
        text = row['TEXT']
        function = function_dict.get(name)
        if function != None:
            function.source_list.extend(compare.split_source(text))
        else:
            function = bean.Function()
            function.name = name
            function.source_list.extend(compare.split_source(text))
            function_dict[name] = function
    l.extend(function_dict.values())
    return l

def _get_procedures(db):
    l = []
    results = _query(db, SQL_GET_PROCEDURES)
    procedure_dict = {}
    for row in results:
        name = row['NAME']
        text = row['TEXT']
        procedure = procedure_dict.get(name)
        if procedure != None:
            procedure.source_list.extend(compare.split_source(text))
        else:
            procedure = bean.Procedure()
            procedure.name = name
            procedure.source_list.extend(compare.split_source(text))
            procedure_dict[name] = procedure
    l.extend(procedure_dict.values())
    return l

def _get_triggers(db):
    l = []
    results = _query(db, SQL_GET_TRIGGERS)
    trigger_dict = {}
    for row in results:
        name = row['NAME']
        text = row['TEXT']
        trigger = trigger_dict.get(name)
        if trigger != None:
            trigger.source_list.extend(compare.split_source(text))
        else:
            trigger = bean.Trigger()
            trigger.name = name
            trigger.source_list.extend(compare.split_source(text))
            trigger_dict[name] = trigger
    l.extend(trigger_dict.values())
    return l

def _get_indexes(db):
    l = []
    results = _query(db, SQL_GET_INDEXES)
    index_dict = {}
    for row in results:
        index_name = row['INDEX_NAME']
        column_name = row['COLUMN_NAME']
        index = index_dict.get(index_name)
        if index != None:
            index.columns.append(column_name)
        else:
           index = bean.Index()
           index.name = index_name
           index.table_name = row['TABLE_NAME']
           index.columns.append(column_name)
           index.uniqueness = row['UNIQUENESS']
           index.index_type = row['INDEX_TYPE']
           index_dict[index_name] = index
    for index in index_dict.values():
        index.source_list = _get_index_ddl(index)
        l.append(index)
    return l

def _get_pks(db):
    l = []
    results = _query(db, SQL_GET_PKS)
    constraint_dict = {}
    for row in results:
        constraint_name = row['CONSTRAINT_NAME']
        table_name = row['TABLE_NAME']
        column_name = row['COLUMN_NAME']
        constraint = constraint_dict.get(constraint_name)
        if constraint != None:
            constraint.columns.append(column_name)
        else:
           constraint = bean.Constraint()
           constraint.name = constraint_name
           constraint.table_name = table_name
           constraint.columns.append(column_name)
           constraint_dict[constraint_name] = constraint
    for constraint in constraint_dict.values():
        constraint.source_list = _get_primary_key_ddl(constraint)
        l.append(constraint)
    return l

def _get_uks(db):
    l = []
    results = _query(db, SQL_GET_UKS)
    constraint_dict = {}
    for row in results:
        constraint_name = row['CONSTRAINT_NAME']
        table_name = row['TABLE_NAME']
        column_name = row['COLUMN_NAME']
        constraint = constraint_dict.get(constraint_name)
        if constraint != None:
            constraint.columns.append(column_name)
        else:
           constraint = bean.Constraint()
           constraint.name = constraint_name
           constraint.table_name = table_name
           constraint.columns.append(column_name)
           constraint_dict[constraint_name] = constraint
    for constraint in constraint_dict.values():
        constraint.source_list = _get_unique_key_ddl(constraint)
        l.append(constraint)
    return l

def _get_fks(db):
    l = []
    results = _query(db, SQL_GET_FKS)
    constraint_dict = {}
    for row in results:
        constraint_name = row['CONSTRAINT_NAME']
        table_name = row['TABLE_NAME']
        column_name = row['COLUMN_NAME']
        delete_rule = row['DELETE_RULE']
        reference_table_name = row['R_TABLE_NAME']
        reference_column_name = row['R_COLUMN_NAME']
        constraint = constraint_dict.get(constraint_name)
        if constraint != None:
            constraint.columns.append(column_name)
            constraint.reference_columns.append(reference_column_name)
        else:
           constraint = bean.Constraint()
           constraint.name = constraint_name
           constraint.table_name = table_name
           constraint.columns.append(column_name)
           constraint.on_delete_type = delete_rule
           constraint.reference_table_name = reference_table_name
           constraint.reference_columns.append(reference_column_name)
           constraint_dict[constraint_name] = constraint
    for constraint in constraint_dict.values():
        constraint.source_list = _get_foreign_key_ddl(constraint)
        l.append(constraint)
    return l

def _get_checks(db):
    l = []
    results = _query(db, SQL_GET_CHECKS)
    for row in results:
        constraint_name = row['CONSTRAINT_NAME']
        table_name = row['TABLE_NAME']
        condition = row['SEARCH_CONDITION']
        constraint = bean.Constraint()
        constraint.name = constraint_name
        constraint.table_name = table_name
        constraint.condition = condition
        constraint.source_list = _get_check_ddl(constraint)
        l.append(constraint)
    return l    

######################################################
# generate DDL
######################################################
def _get_table_ddl(table):
    strings = []
    strings.append('create table ' + table.name.strip())
    strings.append('(')
    for column in table.columns: 
        strings.append(_get_column_ddl(column))
    last_str = strings[len(strings) - 1]
    strings.pop(len(strings) - 1)
    strings.append(last_str.replace(',', ''))
    strings.append(')')
    strings.append('GO')
    for constraint in table.constraints:
        strings.extend(constraint.source_list)
    strings.append('')
    for index in table.indexes:
        strings.extend(index.source_list)    
    return strings

def _get_column_ddl(column):
    string = '  ' + column.name.strip() + ' ' + _get_data_type_ddl(column)
    if column.default_value != None:
        string += ' default ' + _remove_brackets(column.default_value.strip())
    if 'N' == column.nullable:
        string += ' not null'
    string += ','
    return string

def _get_data_type_ddl(column):
    data_type = column.type
    data_length = column.data_length
    if column.data_length != None and column.data_length > 0:
        data_type += '(' + str(column.data_length) + ')'
    return data_type

def _get_foreign_key_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    strings.append('  foreign key (' + ','.join(constraint.columns) + ') references '
                   + constraint.reference_table_name.strip() + ' (' + ','.join(constraint.reference_columns) + ')')
    if 'NO ACTION' != constraint.on_delete_type.strip():
        last_str = strings[len(strings) - 1]
        strings.pop(len(strings) - 1)
        strings.append(last_str + ' on delete ' + constraint.on_delete_type.strip().lower())
    strings.append('GO')
    return strings

def _get_check_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    #condition may have \n character, so split it to multiple rows
    strs = compare.split_source(constraint.condition.strip())
    if len(strs) == 1:
        strings.append('  check (' + constraint.condition.strip() + ')')
        strings.append('GO')
        return strings
    for i in range(0, len(strs)):
        if i == 0:
            strings.append('  check (' + strs[i])
        elif i == len(strs) - 1:
            strings.append(strs[i] + ')')
            strings.append('GO')
        else: 
            strings.append(strs[i])
    return strings

def _get_unique_key_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    strings.append('  unique (' + ','.join(constraint.columns) + ')')
    strings.append('GO')
    return strings

def _get_primary_key_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    strings.append('  primary key (' + ','.join(constraint.columns) + ')')
    strings.append('GO')
    return strings

def _get_index_ddl(index):
    strings = []
    if index.uniqueness:
        strings.append('create ' + index.index_type.strip().lower() + ' unique index ' + index.name.strip())
    else:
        strings.append('create ' + index.index_type.strip().lower() + ' index ' + index.name.strip())
    strings.append('  on ' + index.table_name.strip() + ' (' + ','.join(index.columns) + ')')    
    strings.append('GO')
    return strings

######################################################
# utility method 
######################################################
#only sql server has this issue. remove all brackets (except function's bracket)
def _remove_brackets(value):
    if value.find('(') == 0:
        value = value[1:]
        value = value[:-1]
        return _remove_brackets(value)
    return value

#get data form SqlServer
def _query(db, sql):
    db.execute_query(sql)
    return list(db)

######################################################
# unit test 
######################################################
def _test():
    get_database('shimosdb', 'wcc', 'sa', 'sa', '1433')
    #db = _mssql.connect(server='shimosdb', user='sa', password='sa', database='wcc')

if __name__ == "__main__":
    _test()
