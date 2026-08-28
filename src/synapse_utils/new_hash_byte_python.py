
import pyodbc 
import os
import re
#from pathlib import Path
from config import UID,PWD

#print(UID)
#print(PWD)


connect_voyix_dedicated = pyodbc.connect(
     Trusted_Connection= 'No',
     UID=UID,
     PWD=PWD,
     Authentication='ActiveDirectoryPassword',
     DATABASE='adleprodsynsp01',
     Driver='{ODBC Driver 18 for SQL Server}',
     #Server='adle-prod-syn-ws01-ondemand.sql.azuresynapse.net'
     Server='adle-prod-syn-ws01.sql.azuresynapse.net'
     
)


#proc_name = input('Enter Proc Name: ') 
#schema_name=input('Enter the Schema Name:')

# for single schema run below statement
#schema_name=['trans_procurement_erp_mrp','trans_purchaseorder_faw_oaxuser']
#schema_name=['trans_entitlement_som_con','trans_entitlement_rsim_rsim31','trans_entitlement_erp_erpprod']
schema_name=['trans_order_losbusiness_manualfiles']
#schema_name=['trans_installedbase_neos_ndfprod']

#schema_name=['trans_installedbase_neos_ndfprod','trans_installedbase_losbusiness_manualfiles','trans_installedbase_erp_erpprod','trans_installedbase_epmt_quickbase','hub_installedbase']

# for mutliple run below statement and comment single schema ones
#schema_name=('trans_purchaseorder_faw_oaxuser','trans_purchaseorder_erp_ap')
print(schema_name)


#schema_list = schema_name if isinstance(schema_name, list) else [schema_name]
#print(schema_list)

absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn/hashbyte"


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
    absolute_path1 = f"{absolute_path}"
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
          #column_names=[]
          hashbytes_code=''
          filtered_column_names=''
          variations = ["as hash_key", "AS hash_key", "as [hash_key]", "AS [hash_key]"]
          end_idx = -1
          for variation in variations:
               end_idx = data[0].find(variation)
               print(end_idx)
               if end_idx != -1:
                    print(f"Found '{variation}' at index {end_idx}")
                    start_idx = data[0].rfind("hashbytes('sha2_256',", 0, end_idx)
                    hashbytes_code = data[0][start_idx:end_idx]
                    print(hashbytes_code)
                    break
               
          if end_idx == -1:
               print("No variation of 'hash_key' found.")       
         # start_idx = data[0].find("hashbytes('sha2_256',")
          #end_idx = data[0].find("as VARBINARY(32)) as hash_key", start_idx)
         # start_idx = data[0].find("hashbytes('sha2_256',")
         # end_idx = data[0].find("as hash_key", start_idx)
          # end_idx = data[0].find("as hash_key")
          # end_idx3 = data[0].find("AS hash_key")
          # end_idx1 = data[0].find("as [hash_key]")
          # end_idx2 = data[0].find("AS [hash_key]")
          # print(y[0])
          # print("old",end_idx)
          # if end_idx==-1 and end_idx1!=-1 :
          #      end_idx = data[0].find("as [hash_key]")
          #      print("New1",end_idx)
          #      start_idx = data[0].rfind("hashbytes('sha2_256',", 0, end_idx)
          #      #hashbytes_code = data[0][start_idx:end_idx + len("as [hash_key]")]
          #      hashbytes_code = data[0][start_idx:end_idx]
          #      print(hashbytes_code)
          # elif end_idx1==-1 and end_idx2!=-1 :
          #      end_idx = data[0].find("AS [hash_key]")
          #      print("New",end_idx)
          #      start_idx = data[0].rfind("hashbytes('sha2_256',", 0, end_idx)
          #      #hashbytes_code = data[0][start_idx:end_idx + len("as [hash_key]")]
          #      hashbytes_code = data[0][start_idx:end_idx]
          #      print(hashbytes_code)
          # elif end_idx2==-1 and end_idx3!=-1 :
          #      end_idx = data[0].find("AS hash_key")
          #      print("New",end_idx)
          #      start_idx = data[0].rfind("hashbytes('sha2_256',", 0, end_idx)
          #      #hashbytes_code = data[0][start_idx:end_idx + len("as [hash_key]")]
          #      hashbytes_code = data[0][start_idx:end_idx]
          # else:
          #      #end_idx = data[0].find("as hash_key")
          #      start_idx = data[0].rfind("hashbytes('sha2_256',", 0, end_idx)
          #      hashbytes_code = data[0][start_idx:end_idx + len("as hash_key")]
          #hashbytes_code = data[0][start_idx:end_idx]
          #print("Hashbytes Code:", hashbytes_code)

          #if hashbytes_code==None:
          #     break
          column_pattern = re.compile(r"\[([^\]]+)\]")
          column_names = column_pattern.findall(hashbytes_code)
          filtered_column_names = [name for name in column_names if name.lower() not in ['decimal', 'varchar']]
          print("columnName-", filtered_column_names)
          if column_names==[]:
               #column_pattern = re.compile(r"\[([^\]]+)\]")
               column_pattern = re.compile(r"\bcoalesce\s*\(\s*([a-zA-Z0-9_]+)")
               column_names = column_pattern.findall(hashbytes_code)
               filtered_column_names = [name for name in column_names if name.lower() not in ['decimal', 'varchar']]
               print("new column name",filtered_column_names)

          
          #print(column_names)
          #print(hashbytes_code)
          #print("tablename-", y[0], "hash_key attributes", column_names)
          with open(f'{absolute_path1}/{x}.txt','a',encoding='utf-8',newline='') as hash_file:
               hash_file.write(f"{y[0]} | {', '.join(filtered_column_names)}\n")
          #print(data)
#write the file in .sql file
          #with open(f'{absolute_path1}/{x[0]}.sql','w',encoding='utf-8',newline='') as sql_file:
           #   sql_file.write(data[0])
            #  print(f'File has been written to {x[0]}.sql')


connect_voyix_dedicated.close()
