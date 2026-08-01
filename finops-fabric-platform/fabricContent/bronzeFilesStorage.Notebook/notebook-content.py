# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "87473749-1a99-48bb-8daa-659415d58046",
# META       "default_lakehouse_name": "Bronze",
# META       "default_lakehouse_workspace_id": "e3bf5bc5-4896-4874-a9a1-86628856bc54",
# META       "known_lakehouses": [
# META         {
# META           "id": "87473749-1a99-48bb-8daa-659415d58046"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

#create new file storage directory to cost amoritzed files, 
#so we have historic data in our lakehouse
from datetime import datetime, timedelta

from notebookutils import mssparkutils


# Fetch the current active lakehouse metadata

lakehouse_info_bronze = mssparkutils.lakehouse.get("Bronze") 

# Extract IDs
workspace_id = lakehouse_info_bronze.workspaceId

lakehouse_id_bronze = lakehouse_info_bronze.id

print(f"Workspace ID: {workspace_id}")

print(f"Lakehouse ID bronze: {lakehouse_id_bronze}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Explicit absolute path using your specific workspace and lakehouse IDs

path_str_date = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_bronze}/Files/CostExports/CostExports/Finopsdaily/finops-amortized-cost/"

sc = spark.sparkContext
conf = sc._jsc.hadoopConfiguration()
path_obj_date = sc._jvm.org.apache.hadoop.fs.Path(path_str_date)
fs_date = path_obj_date.getFileSystem(conf)
status_list_date = fs_date.listStatus(path_obj_date)
folder_name_date = [status.getPath().getName() for status in status_list_date if status.isDirectory()]



#iterate the []
for x in folder_name_date:
    x   
folder_name_date=x 


#we have to find the date value  first to add to the path to find the guid 

path_str_guid = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_bronze}/Files/CostExports/CostExports/Finopsdaily/finops-amortized-cost/{folder_name_date}/"
path_obj_guid = sc._jvm.org.apache.hadoop.fs.Path(path_str_guid)
fs_guid = path_obj_guid.getFileSystem(conf)
status_list_guid = fs_guid.listStatus(path_obj_guid)
folder_name_guid = [status.getPath().getName() for status in status_list_guid if status.isDirectory()]

#iterate the []
for x in folder_name_guid:
    x   
folder_name_guid=x 


print("available date folder:", folder_name_date )
print("available GUID folder :", folder_name_guid )


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#writing CostExports folder into folder call datastorage 

BRONZE_CSV_PATH = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_bronze}/Files/CostExports/CostExports/Finopsdaily/finops-amortized-cost/"
print(BRONZE_CSV_PATH)

#creating the folder

# Specify your folder path within the Lakehouse files directory
# Example: abfss://... or the relative Spark path
folder_path = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_bronze}/Files/CostDatastorage"

# Alternatively, if working inside an attached Lakehouse context, you can use relative paths:
# folder_path = "Files/your_folder_name"

sc = spark.sparkContext
conf = sc._jsc.hadoopConfiguration()
path = sc._jvm.org.apache.hadoop.fs.Path(folder_path)
fs = path.getFileSystem(conf)

# Check if the folder exists, and create it if it doesn't
if not fs.exists(path):
    fs.mkdirs(path)
    print(f"Folder created successfully: {folder_path}")
else:
    print(f"Folder already exists: {folder_path}")




# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datetime import datetime, timedelta

# 1. Get current date string for the folder (e.g., "2026-08-01")
previousdate_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# 2. Construct the date-partitioned folder path
date_folder_path = f"{folder_path.rstrip('/')}/{previousdate_str}"

# 3. Check if the folder for today already exists
sc = spark.sparkContext
conf = sc._jsc.hadoopConfiguration()
Path = sc._gateway.jvm.org.apache.hadoop.fs.Path

dest_path = Path(date_folder_path)
fs = dest_path.getFileSystem(conf)

if fs.exists(dest_path):
    print(f"Folder for today ({previousdate_str}) already exists. Skipping data ingestion.")
else:
    # Create the date folder
    fs.mkdirs(dest_path)
    print(f"Created new folder for today: {date_folder_path}")
    
    # 4. Perform your data copy or write operation here
    src_path = Path(f"{BRONZE_CSV_PATH}")
    FileUtil = sc._gateway.jvm.org.apache.hadoop.fs.FileUtil
    FileUtil.copy(src_path.getFileSystem(conf), src_path, dest_path.getFileSystem(conf), dest_path, False, conf)
    print("Data ingested successfully into today's folder!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
