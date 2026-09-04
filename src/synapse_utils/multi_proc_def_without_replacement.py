
import pyodbc 
import os
import re
#from pathlib import Path
from config import UID,PWD

print(UID)
print(PWD)


connect_voyix_dedicated = pyodbc.connect(
     Trusted_Connection= 'No',
     UID=UID,
     PWD=PWD,
     Authentication='ActiveDirectoryPassword',
     DATABASE='adledevsynsp06',
     Driver='{ODBC Driver 18 for SQL Server}',
     #Server='adle-prod-syn-ws01-ondemand.sql.azuresynapse.net'
     Server='adle-dev-syn-ws03.sql.azuresynapse.net'
     
)


#proc_name = input('Enter Proc Name: ')
#schema_name=input('Enter the Schema Name:')
#schema_name=('pub_supply_chain_analytics','pub_procurement_certified_data_cubes')
schema_name=('trans_procurement_faw_oaxuser','hub_supplier')
print(schema_name)
absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn/faw/code_extraction"


for x in schema_name:
    print(x)
    schema_id=f"""select schema_id from sys.schemas where name='{x}'"""
    cursor = connect_voyix_dedicated.cursor()
    cursor = cursor.execute(schema_id)
    schema_ids = cursor.fetchall()
    print(schema_ids)
    schema_idss=schema_ids[0][0]
    print(schema_idss)
    proc_list=f"""select distinct name from sys.procedures
    where schema_id={schema_idss}"""
    cursor = connect_voyix_dedicated.cursor()
    cursor = cursor.execute(proc_list)
    proc_list = cursor.fetchall()
    absolute_path1 = f"{absolute_path}/{x}"
    print(absolute_path1)
    if not os.path.exists(absolute_path1):
         os.makedirs(absolute_path1)
    #print(proc_list)
    for y in proc_list:
          query = f"""SELECT distinct sm.definition
          from sys.sql_modules sm 
          join sys.procedures p 
          on sm.object_id = p.object_id
          join sys.schemas s 
          on p.schema_id = {schema_idss}
          where p.name = '{y[0]}'"""
          cursor = connect_voyix_dedicated.cursor()
          cursor = cursor.execute(query)
          data = cursor.fetchall()
          data = data[0]
          #New_code_for_replacement
          #definition = data
          #old_value = "trans_purchaseorder_faw_oaxuser"
          #new_value = "trans_procurement_faw_oaxuser"
          #original_text = data[0][0]   # from your SQL fetch
          # re.IGNORECASE makes it case-insensitive
          #print(original_text)
          #updated_definition = re.sub(old_value, new_value, original_text, flags=re.IGNORECASE)


#print(data)
#write the file in .sql file
          with open(f'{absolute_path1}/{y[0]}.sql','w',encoding='utf-8',newline='') as sql_file:
              sql_file.write(data[0])
              print(f'File has been written to {y[0]}.sql')
        





connect_voyix_dedicated.close()