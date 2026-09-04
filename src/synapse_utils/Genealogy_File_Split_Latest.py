import pyodbc
import os
import pandas as pd
from config import UID, PWD
import urllib.parse
from sqlalchemy import create_engine


import logging

logging.basicConfig(level=logging.DEBUG)



# Define the connection string
#connection_string = f"mssql+pyodbc://{UID}:{PWD}@adle-prod-syn-ws01.sql.azuresynapse.net/adleprodsynsp01?driver=ODBC+Driver+18+for+SQL+Server&Authentication=ActiveDirectoryPassword"
connection_string = f"mssql+pyodbc://{UID}:{PWD}@adle-prod-syn-ws01.sql.azuresynapse.net/adleprodsynsp01?driver=ODBC+Driver+18+for+SQL+Server&Authentication=ActiveDirectoryPassword"
print(connection_string)
# Create a SQLAlchemy engine
#engine = create_engine(connection_string)

"""params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER=adle-prod-syn-ws01.sql.azuresynapse.net,1433;DATABASE=adleprodsynsp01;UID={UID};PWD={PWD};Authentication='ActiveDirectoryPassword';Trusted_Connection='No'"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")"""

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER=adle-prod-syn-ws01.sql.azuresynapse.net,1433;DATABASE=adleprodsynsp01;UID={UID}@adle-prod-syn-ws01;PWD={PWD}"
)


params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER=adle-prod-syn-ws01.sql.azuresynapse.net,1433;"
    f"DATABASE=adleprodsynsp01;"
    f"UID={UID};"
    f"PWD={PWD};"
    f"Encrypt=yes;"
    f"Authentication=ActiveDirectoryPassword;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

#engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Set up the connection
"""connect_voyix_dedicated = pyodbc.connect(
    Trusted_Connection='No',
    UID=UID,
    PWD=PWD,
    Authentication='ActiveDirectoryPassword',
    DATABASE='adleprodsynsp01',
    Driver='{ODBC Driver 18 for SQL Server}',
    Server='adle-prod-syn-ws01.sql.azuresynapse.net'
)"""

# Define the query
table_select = f"""select distinct transaction_id, invtry_org_id, primary_item_id, primary_unformated_item_id, parent_serial_nbr, child_part_nbr, child_serial_nbr, feature_pid_id, ncr_part_uid, loc_id, type, schedule, class, creation_date_time_utc, transaction_date_time_utc 
from [hub_manufacturing].[dim_external_genealogy_part] 
where loc_id in ( 'USI-GDL', 'USI-TW', 'ECN-BUD' ) 
and adle_transaction_code<>'D'"""

# Define the output path
absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn/Genealogy_data_split"
if not os.path.exists(absolute_path):
    os.makedirs(absolute_path)

# Define the chunk size
chunksize = 1000000
i = 0

# Fetch data in chunks and write each chunk to a separate Excel file
for chunk in pd.read_sql(table_select,engine, chunksize=chunksize):
    chunk.to_excel(f'{absolute_path}/Genealogy_hist_file_{i+1}.xlsx', index=False)
    print(f'{absolute_path}/Genealogy_hist_file_{i+1}.xlsx')
    i += 1

# Close the database connection
#connect_voyix_dedicated.close()