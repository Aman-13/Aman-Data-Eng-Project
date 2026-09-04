import pyodbc
from config import UID, PWD
from databricks import sql
import pandas as pd
import os

# Define constants
catalog_name = 'vyxdbsucqas'
absolute_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn/synapse_databrcks_cmpr"

# Establish connections
connect_voyix_dev_dedicated = pyodbc.connect(
    Trusted_Connection= 'No',
    UID=UID,
    PWD=PWD,
    Authentication='ActiveDirectoryPassword',
    DATABASE='adledevsynsp06',
    Driver='{ODBC Driver 18 for SQL Server}',
    Server='adle-dev-syn-ws03.sql.azuresynapse.net'
)
connect_databricks_UAT = sql.connect(
    server_hostname='adb-932452520638701.1.azuredatabricks.net',
    http_path='/sql/1.0/warehouses/4f02570ab349ce2c',
    access_token='access_token_key'
)

# Get user input
table_schema = input('Enter Syanpse hub Schema Name: ')
table_name = input('Enter the table name: ')
databricks_schema = input('Enter the databricks name: ')
#Sortng_columns = input('Enter the sorting columns (comma separated): ').split(',')
#Sortng_columns = [col.strip() for col in Sortng_columns]
Sortng_columns=input('Enter the sorting_column (comma separated): ')
Sortng_columns_list = [col.strip() for col in Sortng_columns.split(',')]
print(Sortng_columns)

# Fetch columns
column_select = f"""select column_name from INFORMATION_SCHEMA.COLUMNS 
                    WHERE table_schema='{table_schema}' and table_name='{table_name}' 
                    and (column_name not in ('adls_extract_ind', 'pipeline_name', 'pipeline_run_id', 
                    'pipeline_trigger_name', 'pipeline_trigger_id', 'pipeline_trigger_type', 
                    'pipeline_trigger_date_time_utc', 'hub_load_date_time_utc', 'pub_load_date_time_utc', 
                    'gold_load_date_time_utc') and (column_name not like '%surr_key') and (column_name not like '%hash_key')) 
                    order by ordinal_position"""
cursor = connect_voyix_dev_dedicated.cursor()
column_def = cursor.execute(column_select).fetchall()
column_names = [col[0] for col in column_def]
column_string = ", ".join(column_names)

# Fetch Synapse data
synapse_table_sel_def = f"""select top 1000000 {column_string} from {table_schema}.{table_name} order by {Sortng_columns}"""
#synapse_rslt = pd.read_sql(synapse_table_sel_def, connect_voyix_dev_dedicated)
synapse_select_curson_exec=cursor.execute(synapse_table_sel_def)
raw_data = synapse_select_curson_exec.fetchall()
synapse_rslt = pd.DataFrame([list(row) for row in raw_data], columns=column_names)

# Fetch Databricks data and compare
discrepancy_records = []
cursor_databrcks = connect_databricks_UAT.cursor()
for index, row in synapse_rslt.iterrows():
    #where_clause = ' and '.join([f"{col} = '{row[col]}'" if isinstance(row[col], str) else f"{col} = {row[col]}" for col in Sortng_columns_list])
    #where_clause = ' and '.join([f"{col} = '{row[col].replace("'", "''")}'" if isinstance(row[col], str) else f"{col} = {row[col]}" for col in Sortng_columns_list])
    #where_clause = ' and '.join([f"{col} = \"{row[col].replace('"', '\\"')}\"" if isinstance(row[col], str) else f"{col} = {row[col]}" for col in Sortng_columns_list])
    conditions = []
    for col in Sortng_columns_list:
        val = row[col]
        if isinstance(val, str):
            val = val.replace("'", "''")
            conditions.append(f"{col} = '{val}'")
        else:
            conditions.append(f"{col} = {val}")
    where_clause = ' and '.join(conditions)
    databrcks_table_sel_def = f"""select {column_string} from {catalog_name}.{databricks_schema}.{table_name} 
                                  where {where_clause}"""
    databrcks_rslt = pd.read_sql(databrcks_table_sel_def, connect_databricks_UAT)
    
    if not databrcks_rslt.empty:
        databrcks_row = databrcks_rslt.iloc[0]
        if not row.equals(databrcks_row):
            discrepancy_columns = []
            for col in column_names:
                if pd.isnull(row[col]) and pd.isnull(databrcks_row[col]):
                    continue
                elif row[col] != databrcks_row[col]:
                    discrepancy_columns.append(col)
            
            new_row1 = {"source": "synapse"}
            new_row2 = {"source": "databricks"}
            for col in column_names:
                if col in discrepancy_columns:
                    new_row1[col] = f"**{row[col]}**"
                    new_row2[col] = f"**{databrcks_row[col]}**"
                else:
                    new_row1[col] = row[col]
                    new_row2[col] = databrcks_row[col]
            discrepancy_records.append(new_row1)
            discrepancy_records.append(new_row2)
    else:
        # Handle the case where no matching row is found in Databricks
        new_row1 = {"source": "synapse"}
        new_row2 = {"source": "databricks"}
        for col in column_names:
            new_row1[col] = row[col]
            new_row2[col] = None
        discrepancy_records.append(new_row1)
        discrepancy_records.append(new_row2)

# Save discrepancies to Excel
discrepancy_df = pd.DataFrame(discrepancy_records)
if not os.path.exists(absolute_path):
    os.makedirs(absolute_path)
with pd.ExcelWriter(f'{absolute_path}/{table_name}.xlsx', engine='xlsxwriter') as writer:
    discrepancy_df.to_excel(writer, index=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    for col in range(len(discrepancy_df.columns)):
        for row in range(len(discrepancy_df)):
            cell_value = discrepancy_df.iloc[row, col]
            if "**" in str(cell_value):
                worksheet.write(row + 1, col, cell_value, format)

# Close connections
cursor_databrcks.close()
connect_databricks_UAT.close()
cursor.close()
connect_voyix_dev_dedicated.close()
