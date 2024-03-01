#!/usr/bin/env python
# Main Service
import sqlite3
import constant
import result
import compare
import cPickle as pickle

DB_NAME = 'db/db'

def _query(sql, param):
    db = None
    rows = []
    try:
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        cursor.execute(sql, param)
        for c in cursor.fetchall():
            row = {}
            for i in range(len(c)):
                row[cursor.description[i][0]] = c[i]
            rows.append(row)
    except:
        raise
    finally:
        if db != None:
            db.close()
    return rows

def _execute(sql, param):
    db = None
    try:
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        cursor.execute(sql, param)
        db.commit()
    except:
        raise        
    finally:
        if db != None:
            db.close()    

def get_data_source(db_type):
    return _query('SELECT * FROM TB_DATA_SOURCE WHERE db_type=?', (db_type,))

def save_data_source(data_source):
    count = _query('SELECT count(*) num FROM TB_DATA_SOURCE WHERE name=?', (data_source.name,))[0]
    if count['num'] > 0:
        _execute('UPDATE TB_DATA_SOURCE SET host_name=?,db_name=?,user_name=?,password=?,port=? WHERE name=?',
                (data_source.host_name,data_source.db_name,data_source.user_name,data_source.password,data_source.port,data_source.name))
    else:
        _execute('INSERT INTO TB_DATA_SOURCE(name,host_name,db_name,user_name,password,port,db_type) VALUES (?,?,?,?,?,?,?)',
                 (data_source.name,data_source.host_name,data_source.db_name,data_source.user_name,data_source.password,data_source.port,data_source.db_type))

def delete_data_source(name):
    _execute('DELETE FROM TB_DATA_SOURCE WHERE name=?', (name,))

def get_compared_result():
    return _query('SELECT ID,MEMO,CREATED_TIME FROM TB_COMPARED_RESULT', ())

def delete_compared_result(r_id):
    _execute('DELETE FROM TB_COMPARED_RESULT WHERE id=?', (r_id,))

def get_compared_result_detail(r_id):
    result = _query('SELECT * FROM TB_COMPARED_RESULT WHERE id=?', (r_id,))[0] 
    #deserialize ComparedResult from database  
    result['CONTENT'] = pickle.loads(str(result['CONTENT']))
    return result

def save_compared_result(memo, compared_result):
    #serialize ComparedResult to database
    _execute('INSERT INTO TB_COMPARED_RESULT(content, memo) VALUES (?,?)', (pickle.dumps(compared_result), memo))
    
def do_compare(ds):
    if ds.db_type == constant.DB_TYPE_ORACLE:
        import oracle_handler as handler
    elif ds.db_type == constant.DB_TYPE_SQLSERVER:
        import sqlserver_handler as handler
    owner_db = handler.get_database(
    ds.owner_host_name, 
    ds.owner_db_name, 
    ds.owner_user_name, 
    ds.owner_password, 
    ds.owner_port)
    target_db = handler.get_database(
    ds.target_host_name, 
    ds.target_db_name, 
    ds.target_user_name, 
    ds.target_password, 
    ds.target_port)
    
    resultBean = result.DatabaseResultBean()
    resultBean.owner = owner_db
    resultBean.target = target_db
    resultBean.db_type = ds.db_type
    resultBean.tables = compare.compare_object(owner_db.tables, target_db.tables)
    resultBean.views = compare.compare_object(owner_db.views, target_db.views)
    resultBean.functions = compare.compare_object(owner_db.functions, target_db.functions)
    resultBean.procedures = compare.compare_object(owner_db.procedures, target_db.procedures)
    resultBean.triggers = compare.compare_object(owner_db.triggers, target_db.triggers)
    if ds.db_type == constant.DB_TYPE_ORACLE:
        resultBean.sequences = compare.compare_object(owner_db.sequences, target_db.sequences)
        resultBean.packages = compare.compare_object(owner_db.packages, target_db.packages)
        resultBean.package_bodies = compare.compare_object(owner_db.package_bodies, target_db.package_bodies)
        resultBean.materialized_views = compare.compare_object(owner_db.materialized_views, target_db.materialized_views)
    return resultBean 
    
