# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "038d934f-db99-44f1-bd39-da7a7f68f078",
# META       "default_lakehouse_name": "Silver",
# META       "default_lakehouse_workspace_id": "e3bf5bc5-4896-4874-a9a1-86628856bc54",
# META       "known_lakehouses": [
# META         {
# META           "id": "038d934f-db99-44f1-bd39-da7a7f68f078"
# META         },
# META         {
# META           "id": "87473749-1a99-48bb-8daa-659415d58046"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

from notebookutils import mssparkutils


# Fetch the current active lakehouse metadata
lakehouse_info_silver = mssparkutils.lakehouse.get("Silver")
lakehouse_info_bronze = mssparkutils.lakehouse.get("Bronze") 

# Extract IDs
workspace_id = lakehouse_info_silver.workspaceId
lakehouse_id_silver = lakehouse_info_silver.id
lakehouse_id_bronze = lakehouse_info_bronze.id

print(f"Workspace ID: {workspace_id}")
print(f"Lakehouse ID silver: {lakehouse_id_silver}") 
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

# ==========================================
# 1. IMPORTS & CONFIGURATION
# ==========================================
from pyspark.sql.functions import (
    col, from_json, to_date, current_timestamp, 
    md5, coalesce, lit
)
from pyspark.sql.types import MapType, StringType, DecimalType

# Source remains in Bronze (or wherever your raw files 

# Construct the dynamic Bronze CSV path using the variables
BRONZE_CSV_PATH = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_bronze}/Files/CostExports/CostExports/Finopsdaily/finops-amortized-cost/{folder_name_date}/{folder_name_guid}/*.csv.gz"

# Construct the Silver ABFS paths dynamically using the workspace and Silver lakehouse IDs
SILVER_ABFS_FILES = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_silver}/Files"
SILVER_ABFS_TABLES = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id_silver}/Tables"



STAGING_CSV_FILES_PATH = f"{SILVER_ABFS_FILES}/silver_staged_csv/amortized_cost"
TARGET_TABLE_LOCATION = f"{SILVER_ABFS_TABLES}/dbo/silver_amortized_cost"
TARGET_TABLE_NAME = "dbo.silver_amortized_cost"

print(f"Reading CSV from: {BRONZE_CSV_PATH}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 2. READ CSV FROM BRONZE
# ==========================================
df_raw = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .option("quote", '"')
    .option("escape", '"')
    .csv(BRONZE_CSV_PATH)
)

# Standardize column headers to lowercase
df_lowercase = df_raw.toDF(*[c.lower() for c in df_raw.columns])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# ==========================================
# 3. TRANSFORMATIONS & TYPE CASTING
# ==========================================
tag_map_schema = MapType(StringType(), StringType())


df_transformed = (
    df_lowercase
    .withColumn("serviceperiodenddate", to_date(col("serviceperiodenddate")))
    .withColumn("serviceperiodstartdate", to_date(col("serviceperiodstartdate")))
    .withColumn("usagedate", to_date(col("date"), "MM/dd/yyyy"))
    
    .withColumn("unitprice", col("unitprice").cast(DecimalType(18, 8)))
    .withColumn("billedcost", col("costinbillingcurrency").cast(DecimalType(18, 8)))
    .withColumn("effectivecost", col("effectiveprice").cast(DecimalType(18, 8)))
    .withColumn("paygcost", col("paygcostinbillingcurrency").cast(DecimalType(18, 8)))
    .withColumn("usagequantity", col("quantity").cast(DecimalType(18, 8)))
    
    .withColumn("costcentercode", coalesce(col("costcenter"), lit(None)))
    .withColumn("commitmentid", coalesce(col("reservationid"), lit(None)))
    
    .withColumn("tags_map", from_json(col("tags"), tag_map_schema))
    .withColumn("tag_environment", col("tags_map").getItem("Environment"))
    .withColumn("tag_costcenter", col("tags_map").getItem("CostCenter"))
    .withColumn("tag_managedby", col("tags_map").getItem("ManagedBy"))
    .withColumn("tag_owner", col("tags_map").getItem("Owner"))
    .withColumn("tag_project", col("tags_map").getItem("Project"))
    
    .withColumn("taghash", md5(coalesce(col("tags"), lit(""))))
    .withColumn("silverprocessedtimestamp", current_timestamp())
    .drop("tags_map")

)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 4. STEP 1: SAVE CSV DIRECTLY TO SILVER LAKEHOUSE FILES
# ==========================================
print(f"Exporting transformed data as CSV to Silver Files: {STAGING_CSV_FILES_PATH}")
(
    df_transformed.write
    .format("csv")
    .mode("overwrite")
    .option("header", "true")
    .save(STAGING_CSV_FILES_PATH)
)
print("CSV successfully written to Silver Files path.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 5. STEP 2: CREATE EXTERNAL/MANAGED TABLE POINTING TO SILVER TABLES
# ==========================================
spark.sql(f"DROP TABLE IF EXISTS {TARGET_TABLE_NAME}")

print(f"Creating table '{TARGET_TABLE_NAME}' in Silver storage location...")

# Read back the staged CSV files from the Silver Files path
df_staged_csv = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(STAGING_CSV_FILES_PATH)
)


# Write out as a Delta table explicitly bound to the Silver Lakehouse Tables path
(
    df_staged_csv.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", TARGET_TABLE_LOCATION)
    .saveAsTable(TARGET_TABLE_NAME)
)

print(f"Successfully created and registered '{TARGET_TABLE_NAME}' in the Silver Lakehouse!")



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 6. SANITY CHECK
# ==========================================
df_check = spark.table(TARGET_TABLE_NAME)
print(f"Total Rows in {TARGET_TABLE_NAME}: {df_check.count()}")
display(df_check.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
