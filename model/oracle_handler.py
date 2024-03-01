#!/usr/bin/python
# Oracle handler
import bean
import compare
import cx_Oracle as oracle

SQL_GET_TABLES = '''
select t.*,u.temporary from user_tab_cols t
inner join user_tables u on t.table_name=u.table_name
where not exists (select 1 from user_mviews m where m.MVIEW_NAME=u.table_name)
order by t.column_id asc'''

SQL_GET_INDEXES = '''
select row_.* from (
select i.INDEX_NAME,i.TABLE_NAME,i.UNIQUENESS,i.INDEX_TYPE,c.COLUMN_NAME,t.index_name flag from user_indexes i
inner join user_ind_columns c on c.index_name=i.index_name
left join user_constraints t on t.index_name=c.index_name
order by i.index_name, c.column_name asc) row_
where row_.flag is null'''

SQL_GET_PKS = '''
SELECT t.constraint_name,t.table_name,c.column_name
FROM user_constraints t
inner JOIN user_cons_columns c ON c.constraint_name=t.constraint_name
WHERE t.generated='USER NAME'
AND t.constraint_type='P'
ORDER BY t.constraint_name,c.column_name ASC'''

SQL_GET_UKS = '''
SELECT t.constraint_name,t.table_name,c.column_name
FROM user_constraints t
inner JOIN user_cons_columns c ON c.constraint_name=t.constraint_name
WHERE t.generated='USER NAME'
AND t.constraint_type='U'
ORDER BY t.constraint_name,c.column_name ASC'''

SQL_GET_FKS = '''
SELECT t.constraint_name,t.delete_rule,t.table_name,c.column_name,cc.column_name r_column_name,cc.table_name r_table_name
FROM user_constraints t
inner JOIN user_cons_columns c ON c.constraint_name=t.constraint_name
inner join user_cons_columns cc ON cc.constraint_name=t.r_constraint_name
WHERE t.generated='USER NAME'
AND t.constraint_type='R'
AND c.position=cc.position
ORDER BY t.constraint_name,c.column_name ASC'''

SQL_GET_CHECKS = '''
SELECT t.constraint_name,t.table_name,c.column_name,t.search_condition
FROM user_constraints t
inner JOIN user_cons_columns c ON c.constraint_name=t.constraint_name
WHERE t.generated='USER NAME'
AND t.constraint_type='C'
ORDER BY t.constraint_name,c.column_name ASC'''

SQL_GET_FUNCTIONS = '''
SELECT name, line, text FROM user_source
WHERE type='FUNCTION' ORDER BY name,line ASC'''

SQL_GET_PROCEDURES = '''
SELECT name, line, text FROM user_source
WHERE type='PROCEDURE' ORDER BY name,line ASC'''

SQL_GET_TRIGGERS = '''
SELECT name, line, text FROM user_source
WHERE type='TRIGGER' ORDER BY name,line ASC'''

SQL_GET_VIEWS = 'SELECT view_name, text FROM user_views order by view_name asc'

SQL_GET_PACKAGES = '''
SELECT name, line, text FROM user_source
WHERE type='PACKAGE' ORDER BY name,line ASC'''

SQL_GET_PACKAGE_BODIES = '''
SELECT name, line, text FROM user_source
WHERE type='PACKAGE BODY' ORDER BY name,line ASC'''

SQL_GET_SEQUENCES = 'SELECT sequence_name FROM user_sequences order by sequence_name asc'

SQL_GET_MVIEWS = 'select * from user_mviews order by MVIEW_NAME asc'

#will be used by Table or MaterializedView
indexes = []

def get_database(host_name, db_name, user_name, password, port):
    db = None
    try:
        db_full_name = oracle.makedsn(host_name, port, db_name)
        db = oracle.connect(str(user_name), str(password), str(db_full_name))
    
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
        database.sequences = _get_sequences(db)
        database.packages = _get_packages(db)
        database.package_bodies = _get_packageBodies(db)
        database.materialized_views = _get_materialized_views(db)
    except:
        raise        
    finally:
        if db != None:
            db.close()
    return database

def _get_tables(db):
    l = []
    results = _query(db, SQL_GET_TABLES)
    global indexes
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
            table.temporary = row['TEMPORARY']
            table_dict[table_name] = table
        column = bean.Column()
        column.table_name = table_name
        column.name = row['COLUMN_NAME']
        column.default_value = row['DATA_DEFAULT']
        column.nullable = row['NULLABLE']
        column.type = row['DATA_TYPE']
        column.data_length = row['DATA_LENGTH']
        column.data_precision = row['DATA_PRECISION']
        table.columns.append(column)
    #set index
    for index in indexes:
        table = table_dict.get(index.table_name)
        #some index may be in Materialized View, So need to judge table is null or not
        if table != None:
            table.indexes.append(index)
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
        view.source_list.append('create or replace VIEW ' + name + ' as')
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
            function.source_list.append(text)
        else:
            function = bean.Function()
            function.name = name
            function.source_list.append('create or replace ' + text)
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
            procedure.source_list.append(text)
        else:
            procedure = bean.Procedure()
            procedure.name = name
            procedure.source_list.append('create or replace ' + text)
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
            trigger.source_list.append(text)
        else:
            trigger = bean.Trigger()
            trigger.name = name
            trigger.source_list.append('create or replace ' + text)
            trigger_dict[name] = trigger
    l.extend(trigger_dict.values())
    return l

def _get_sequences(db):
    l = []
    results = _query(db, SQL_GET_SEQUENCES)
    for row in results:
        name = row['SEQUENCE_NAME']
        sequence = bean.Sequence()
        sequence.name = name
        sequence.source_list.append('create sequence ' + name + ';')
        l.append(sequence)
    return l

def _get_packages(db):
    l = []
    results = _query(db, SQL_GET_PACKAGES)
    package_dict = {}
    for row in results:
        name = row['NAME']
        text = row['TEXT']
        package = package_dict.get(name)
        if package != None:
            package.source_list.append(text)
        else:
            package = bean.Package()
            package.name = name
            package.source_list.append('create or replace ' + text)
            package_dict[name] = package
    l.extend(package_dict.values())
    return l

def _get_packageBodies(db):
    l = []
    results = _query(db, SQL_GET_PACKAGE_BODIES)
    pb_dict = {}
    for row in results:
        name = row['NAME']
        text = row['TEXT']
        pb = pb_dict.get(name)
        if pb != None:
            pb.source_list.append(text)
        else:
            pb = bean.PackageBody()
            pb.name = name
            pb.source_list.append('create or replace ' + text)
            pb_dict[name] = pb
    l.extend(pb_dict.values())
    return l

def _get_materialized_views(db):
    l = []
    results = _query(db, SQL_GET_MVIEWS)
    mview_dict = {}
    for row in results:
        name = row['MVIEW_NAME']
        code = row['QUERY']
        refresh_mode = row['REFRESH_MODE']
        refresh_method = row['REFRESH_METHOD']
        mview = bean.MaterializedView()
        mview.name = name
        mview.refresh_mode = refresh_mode
        mview.refresh_method = refresh_method
        mview.source_list.append('create materialized view ' + name)
        mview.source_list.append('  refresh ' + refresh_mode + ' on ' + refresh_method)
        mview.source_list.append('as')
        mview.source_list.extend(compare.split_source(code.strip()))
        mview.source_list.append(';')
        l.append(mview)
        mview_dict[name] = mview
    #set indexes
    for index in indexes:
        #index column name start with SYS_ is created by system auto
        if index.columns[0].startswith('SYS_'):
            continue
        mview = mview_dict.get(index.table_name)
        #some index may be in Table, So need to judge materializedView is null or not
        if mview != None:
            mview.indexes.append(index)
            mview.source_list.append('')
            mview.source_list.extend(_get_index_ddl(index))
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
    is_temp = 'Y' == table.temporary
    temp_str = ''
    if is_temp:
        temp_str = 'global temporary '
    strings.append('create ' + temp_str + 'table ' + table.name.strip())
    strings.append('(')
    for column in table.columns: 
        strings.append(_get_column_ddl(column))
    last_str = strings[len(strings) - 1]
    strings.pop(len(strings) - 1)
    strings.append(last_str.replace(',', ''))
    temp_str = ');'
    if is_temp:
        temp_str = ') on commit delete rows;'
    strings.append(temp_str)
    strings.append('')
    for constraint in table.constraints:
        strings.extend(constraint.source_list)
    strings.append('')
    for index in table.indexes:
        strings.extend(index.source_list)
    return strings

def _get_column_ddl(column):
    string = '  ' + column.name.strip() + ' ' + _get_data_type_ddl(column)
    if column.default_value != None:
        string += ' default ' + column.default_value.strip()
    if 'N' == column.nullable:
        string += ' not null'
    string += ','
    return string

def _get_data_type_ddl(column):
    data_type = column.type
    data_length = column.data_length
    data_precision = column.data_precision
    ori_types = ['DATE', 'CLOB', 'BLOB', 'FLOAT']
    if 'NUMBER' == data_type and data_length == 22:
        return 'INTEGER'
    elif data_type.startswith('TIMESTAMP') or ori_types.count(data_type) > 0:
        return data_type
    else:
        if data_length != None:
            data_type += '(' + str(data_length)
        if data_precision != None:
            data_type += ',' + str(data_precision)
        data_type += ')'
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
    last_str = strings[len(strings) - 1]
    strings.pop(len(strings) - 1)
    strings.append(last_str + ';')
    return strings

def _get_check_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    #condition may have \n character, so split it to multiple rows
    strs = compare.split_source(constraint.condition.strip())
    if len(strs) == 1:
        strings.append('  check (' + constraint.condition.strip() + ');')
        return strings
    for i in range(0, len(strs)):
        if i == 0:
            strings.append('  check (' + strs[i])
        elif i == len(strs) - 1:
            strings.append(strs[i] + ');')
        else: 
            strings.append(strs[i])
    return strings

def _get_unique_key_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    strings.append('  unique (' + ','.join(constraint.columns) + ');')
    return strings

def _get_primary_key_ddl(constraint):
    strings = []
    strings.append('alter table ' + constraint.table_name.strip() + ' add constraint ' + constraint.name.strip())
    strings.append('  primary key (' + ','.join(constraint.columns) + ');')
    return strings

def _get_index_ddl(index):
    strings = []
    if 'UNIQUE' == index.uniqueness.strip():
        strings.append('create ' + index.index_type.strip().lower() + ' unique index ' + index.name.strip())
    else:
        strings.append('create ' + index.index_type.strip().lower() + ' index ' + index.name.strip())
    strings.append('  on ' + index.table_name.strip() + ' (' + ','.join(index.columns) + ');')        
    return strings

def _query(db, sql):
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(sql)
        rows = []
        for c in cursor.fetchall(): 
            row = {}
            for i in range(len(c)):
                row[cursor.description[i][0]] = c[i]    
            rows.append(row)
    except:
        raise
    finally:
        if cursor != None:
            cursor.close()    
    return rows
