import pyodbc 
import os
#from pathlib import Path
from config import  UID,PWD
#from config import  UID,PWD
#from dotenv  import load_dotenv
#load_dotenv()
#from config import UID,PWD

print(UID)
#print(PWD)


#print(os.getenv('UID'))
connect_voyix_serverless = pyodbc.connect(
    Trusted_Connection= 'No',
    UID=UID,
    PWD=PWD,
    Authentication='ActiveDirectoryPassword',
    DATABASE='adleprodservlessdb01',
    Driver='{ODBC Driver 18 for SQL Server}',
    Server='adle-prod-syn-ws01-ondemand.sql.azuresynapse.net'
)


#schemaname=('hub_manufacturing','pub_manufacturing_certified_data_cubes','hub_product')
schemaname=('hub_product_v')

#schemaname=('hub_manufacturing')

absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn"

#sql_query = f"""select distinct trim(table_schema) as table_schema from INFORMATION_SCHEMA.COLUMNS \n 
#where table_schema in {schemaname}"""
sql_query = f"""select distinct trim(table_schema) as table_schema from INFORMATION_SCHEMA.COLUMNS \n 
where table_schema='{schemaname}'"""
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
         print(x[0])
         if x[0]=='':
             print('null')
         else:
            query1=f"""SELECT TRIM(OBJECT_DEFINITION (OBJECT_ID(N'{schema[0]}.{x[0]}')))AS [Object Definition]"""
            print(query1)
            cursor.execute(query1)
            tbl_ddl = cursor.fetchall()
            data = tbl_ddl[0][0]
            print(data)
            with open(f'{absolute_path1}/{x[0]}.sql','w') as file:
                file.write(data)

connect_voyix_serverless.close()
