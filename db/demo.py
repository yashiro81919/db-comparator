#!/usr/bin/env python
# Create demo data
import sqlite3

def demo():
    cx = sqlite3.connect('db')
    cu = cx.cursor()
    #populate data source
    cu.execute('''insert into TB_DATA_SOURCE(NAME, HOST_NAME, DB_NAME, USER_NAME, PASSWORD, PORT, DB_TYPE)
                    VALUES ('bpora', 'shimosvm2', 'bpora', 'imos', 'bondi', '1521', 'oracle')''')
    cu.execute('''insert into TB_DATA_SOURCE(NAME, HOST_NAME, DB_NAME, USER_NAME, PASSWORD, PORT, DB_TYPE)
                    VALUES ('eni2', 'shimosorcl', 'eni2', 'imos', 'bondi', '1521', 'oracle')''')
    cu.execute('''insert into TB_DATA_SOURCE(NAME, HOST_NAME, DB_NAME, USER_NAME, PASSWORD, PORT, DB_TYPE)
                    VALUES ('petrochina', 'shimosvm2', 'petrochina', 'imos', 'bondi', '1521', 'oracle')''')
    cu.execute('''insert into TB_DATA_SOURCE(NAME, HOST_NAME, DB_NAME, USER_NAME, PASSWORD, PORT, DB_TYPE)
                    VALUES ('wcp sa', 'shimosdb.dev.aspentech.com', '7204s', 'sa', 'sa', '1433', 'sqlserver')''')
    cu.execute('''insert into TB_DATA_SOURCE(NAME, HOST_NAME, DB_NAME, USER_NAME, PASSWORD, PORT, DB_TYPE)
                    VALUES ('wcc', 'shimosdb.dev.aspentech.com', 'wcc', 'sa', 'sa', '1433', 'sqlserver')''')
    #populate sql
    cu.execute('''insert into TB_SQL(SQL)
                    VALUES ('select ''Record Count'' id, count(*) num from UICOMPONENT')''')    
    cu.execute('''insert into TB_SQL(SQL)
                    VALUES ('select ''Record Count'' id, count(*) num from UICOMPONENTRELATIONSHIP')''')  
    cu.execute('''insert into TB_SQL(SQL)
                    VALUES ('select * from MOT order by id')''')     
    cu.execute('''insert into TB_SQL(SQL)
                    VALUES ('select code,originProcess,type,severity,briefMessageKey,detailedMessageKey,resolutionKey,reprocessingFlag,authorisedRoleId from ConditionCataloorder by code')''') 
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select uiCompType,uiCompTypeDesc,prioritySeq,uiCompTypeNote from UIcomponentType order by uiCompType')''') 
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select id,nameKey,required,hidden from Functionality order by id')''') 
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select id,objectType,name,methodName from ObjectDefinition order by id')''') 
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select functionalityId,objectDefinitionId,canRead,canWrite,canExecute from ObjectPermissions order by functionalityId,objectDefinitionId')''') 
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select roleId,functionalityId from RoleFunctionality order by roleId,functionalityId')''')     
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select id,version,name,type from PlanningCalendar order by id')''')      
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select id,version,name,type,beginDate,endDate from PlanningPeriod order by id')''') 
    cu.execute('''insert into TB_SQL(SQL)    
                    VALUES ('select planningCalendarId,planningPeriodId from PCalendarPPeriod order by planningCalendarId,planningPeriodId')''') 

    cx.commit()
    cx.close()

demo()
