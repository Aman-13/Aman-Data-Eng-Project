
import os

import re


def list_sql_files(directory):
    try:
        files = os.listdir(directory)
        sql_files = [file for file in files if file.endswith('.sql')]
        return sql_files
    except FileNotFoundError:
        return f"The directory '{directory}' does not exist."
    except Exception as e:
        return f"An error occurred: {e}"


def extract_hashbytes_attributes(file_path):
    attributes = []
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            #pattern = r"hashbytes\\('sha2_256',\\s*concat\\((.*?)\\)"
            matches = re.findall(r"HASHBYTES\\('sha2_256',\\s*concat\\((.*?)\\)\\)", content, re.IGNORECASE | re.DOTALL)
            matches = re.findall(r"HASHBYTES\\('sha2_256',\\s*(.*?)\\)", content, re.IGNORECASE | re.DOTALL)

            #matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                                attrs = re.findall(r"coalesce\\(([^,]+),", match, re.IGNORECASE)
                                #attrs = re.findall(r"coalesce\\(([^,]+),", block, re.IGNORECASE)
                #attrs = re.findall(r"upper\\(coalesce\\((.*?),\\s*''\\)\\)", match, re.IGNORECASE)
                #attributes.extend(attrs)
                                attributes.extend([attr.strip() for attr in attrs])
                                print(attributes)

                #print(attributes.extend(attrs))
    except Exception as e:
        return f"An error occurred while reading '{file_path}': {e}"
    return attributes


# Replace this with your actual directory path
directory_path = "C:/Users/aa250585/OneDrive - NCR Corporation/Documents/Py_Test/Learn/aman_test_hashbyte"
sql_files_list = list_sql_files(directory_path)
print(sql_files_list)



if isinstance(sql_files_list, list):
    all_attributes = {}
    for file in sql_files_list:
        file_path = os.path.join(directory_path, file)
        file_path = file_path.replace("\\", "/")
        print(file_path)
        attributes = extract_hashbytes_attributes(file_path)
        all_attributes[file] = attributes
        #print("Attributes used within HASHBYTES function calls:")
        #for file, attrs in all_attributes.items():
        #    print(f"\nFile: {file}")
        #    for attr in attrs:
        #        print(f" - {attr}")
        
        if isinstance(attributes, list):
            for attr in attributes:
                print(f" - {attr}")
        else:
            print(f"Error: {attributes}")

else:
    print(sql_files_list)





