
import pyodbc 
import os
#from pathlib import Path
from config import  UID,PWD
from config import  UID,PWD
from dotenv  import load_dotenv
load_dotenv()

print(os.getenv('UID'))
connect_voyix_serverless = pyodbc.connect(
     Trusted_Connection= 'No',
     UID=os.getenv('UID'),
     PWD=os.getenv('PWD'),
     Authentication='ActiveDirectoryPassword',
     DATABASE='adleprodservlessdb01',
     Driver='{ODBC Driver 18 for SQL Server}',
     Server='adle-prod-syn-ws01-ondemand.sql.azuresynapse.net'
)


schemaname=('hub_manufacturing','pub_manufacturing_certified_data_cubes','hub_product')

#schemaname=('hub_manufacturing')

absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn"

sql_query = f"""select distinct trim(table_schema) as table_schema from INFORMATION_SCHEMA.COLUMNS \n 
where table_schema in {schemaname}"""
print(sql_query)
cursor = connect_voyix_serverless.cursor()
cursor.execute(sql_query)
schema_rows = cursor.fetchall()
print(schema_rows)



for schema in schema_rows:
    sql_query1 = f"""select distinct trim(table_name) as table_name from INFORMATION_SCHEMA.COLUMNS \n
    where table_schema='{schema[0]}'"""
    print(sql_query1)
    cursor = connect_voyix_serverless.cursor()
    cursor.execute(sql_query1)
    table_rows = cursor.fetchall()
    print(table_rows)
    absolute_path1 = f"{absolute_path}/{schema[0]}"
    print(absolute_path1)
    if not os.path.exists(absolute_path1):
         os.makedirs(absolute_path1)

    for x in table_rows:
         print(x)
         query1=f"""with cte as ( \n
         SELECT
         trim(c.table_schema) as table_schema,
         TRIM(c.table_name) as table_name,c.column_name,
    c.data_type,
    c.character_maximum_length,
    CASE 
    WHEN UPPER(c.data_type) = 'DECIMAL' THEN '['+c.column_name+']'+ ' ' + '['+c.data_type+']' + ' (' + COALESCE(CAST(c.numeric_precision AS VARCHAR(20)),'') +','+COALESCE(CAST(c.numeric_scale AS VARCHAR(20)),'')+') '+COALESCE(CAST(' COLLATE '+ c.collation_name AS VARCHAR(50)),'')
    WHEN UPPER(c.data_type) = 'VARCHAR' or UPPER(c.data_type) = 'NVARCHAR' or UPPER(c.data_type) = 'CHAR' OR UPPER(c.data_type) = 'VARBINARY' THEN '['+c.column_name+']'+ ' ' + '['+c.data_type+']'+'('+CAST(c.character_maximum_length AS VARCHAR(20))+')'+COALESCE(CAST(' COLLATE '+ c.collation_name AS VARCHAR(50)),'')
    WHEN UPPER(c.data_type) = 'DATETIME2'  THEN '['+c.column_name+']'+ ' ' + '['+c.data_type+']'+'(7)'+COALESCE(CAST(' COLLATE '+c.collation_name AS VARCHAR(50)),'')
    ELSE '['+c.column_name+']'+ ' ' + '['+c.data_type+']'+COALESCE(CAST(' COLLATE '+c.collation_name AS VARCHAR(50)),'') END as derivedcolumn,
    et.location,
    eff.name as ext_file_format,
    eds.name as ext_data_source,
    C.ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.COLUMNS c
    LEFT JOIN sys.external_tables et
    ON TRIM(c.table_name) = TRIM(et.name)
    LEFT JOIN sys.external_file_formats eff 
    on et.file_format_id = eff.file_format_id
    LEFT JOIN sys.external_data_sources eds 
    on eds.data_source_id = et.data_source_id
       WHERE c.table_schema = '{schema[0]}'
   and C.TABLE_NAME='{x[0]}'
    GROUP BY 
    trim(c.table_schema),
    TRIM(c.table_name),
    c.column_name,
    c.data_type,
    c.character_maximum_length,
    et.location,
    eff.name,
    eds.name,
    c.numeric_precision,
    c.numeric_scale,
    c.collation_name,
    c.table_name,
    c.ORDINAL_POSITION
    ),
    cte1 as ( 
    select  table_schema,c.table_name,c.ext_data_source,c.location,c.ext_file_format,
    STRING_AGG(CONVERT(VARCHAR(MAX),c.derivedcolumn),',\n')  WITHIN GROUP (ORDER BY c.table_name asc,c.ORDINAL_POSITION asc) as column_merger
     from cte c
     group by table_schema,c.table_name,c.ext_data_source,c.location,c.ext_file_format
  )
select 
concat( 'IF EXISTS ( SELECT * FROM sys.external_tables WHERE object_id = OBJECT_ID(''',c.table_schema,'.',c.table_name,''')) ',CHAR(13),
    'DROP EXTERNAL TABLE ',c.table_schema,'.',c.table_name, CHAR(13),
     'go','
CREATE EXTERNAL TABLE ',c.table_schema,'.',c.table_name,' (',column_merger,' ) ', CHAR(13),
--c.ext_data_source,c.location,c.ext_file_format,
 'WITH (
  DATA_SOURCE = [',ext_data_source,'],
    LOCATION = N''',location,''',
   FILE_FORMAT = [',ext_file_format,'] 
   )
;'
) as external_table_script
 from cte1 c"""
         cursor.execute(query1)
         tbl_ddl = cursor.fetchall()
         data = tbl_ddl[0][0]
         with open(f'{absolute_path1}/{x[0]}.sql','w') as file:
             file.write(data)

connect_voyix_serverless.close()



 




