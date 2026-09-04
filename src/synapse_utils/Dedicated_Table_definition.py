import pyodbc 
import os
#from pathlib import Path
from config import  UID,PWD
from conpyofig import  UID,PWD
from dotenv  import load_dotenv
load_dotenv()

print(os.getenv('UID'))
connect_voyix_dedicated = pyodbc.connect(
    Trusted_Connection= 'No',
    UID=UID,
    PWD=PWD,
    Authentication='ActiveDirectoryPassword',
    DATABASE='adleprodsynsp01',
    Driver='{ODBC Driver 18 for SQL Server}',
    Server='adle-prod-syn-ws01.sql.azuresynapse.net'
)


schemaname='trans_procurement_erp_po'

#schemaname=('hub_manufacturing')

absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn/table"

sql_query = f"""select distinct trim(table_schema) as table_schema from INFORMATION_SCHEMA.COLUMNS \n 
where table_schema in ('{schemaname}')"""
print(sql_query)
cursor = connect_voyix_dedicated.cursor()
cursor.execute(sql_query)
schema_rows = cursor.fetchall()
print(schema_rows)



for schema in schema_rows:
    sql_query1 = f"""select distinct trim(table_name) as table_name from INFORMATION_SCHEMA.COLUMNS \n
    where table_schema='{schema[0]}'"""
    print(sql_query1)
    cursor = connect_voyix_dedicated.cursor()
    cursor.execute(sql_query1)
    table_rows = cursor.fetchall()
    print(table_rows)
    absolute_path1 = f"{absolute_path}/{schema[0]}"
    print(absolute_path1)
    if not os.path.exists(absolute_path1):
         os.makedirs(absolute_path1)
    for x in table_rows:
         print(x[0])
         if x[0]=='':
             print('null')
         else:
            query1=f"""SELECT 
    'CREATE TABLE ' + TABLE_SCHEMA + '.' + TABLE_NAME + ' (' + 
    STRING_AGG(
    + CHAR(10) + 
        CAST(
            COLUMN_NAME + ' ' + 
            DATA_TYPE + 
            CASE 
                WHEN DATA_TYPE IN ('varchar', 'char', 'nvarchar', 'nchar') THEN '(' + CONVERT(VARCHAR(10), CHARACTER_MAXIMUM_LENGTH) + ')'
                WHEN DATA_TYPE IN ('decimal', 'numeric') THEN '(' + CONVERT(VARCHAR(10), NUMERIC_PRECISION) + ', ' + CONVERT(VARCHAR(10), NUMERIC_SCALE) + ')'
                ELSE ''
            END + 
            CASE 
                WHEN IS_NULLABLE = 'NO' THEN ' NOT NULL'
                ELSE ' NULL'
            END 
        AS NVARCHAR(MAX)), 
        ',' 
                ) +  
    ');' AS TableDefinition
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = '{schema[0]}' 
    AND TABLE_NAME = '{x[0]}'
GROUP BY 
    TABLE_SCHEMA, TABLE_NAME;
"""
            #print(query1)
            cursor.execute(query1)
            tbl_ddl = cursor.fetchall()
            data = tbl_ddl[0][0]
            #print(data)
            with open(f'{absolute_path1}/{x[0]}.sql','w') as file:
                file.write(data)

connect_voyix_dedicated.close()

