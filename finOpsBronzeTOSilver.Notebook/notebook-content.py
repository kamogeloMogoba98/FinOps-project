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

# Source remains in Bronze (or wherever your raw files are)
BRONZE_CSV_PATH = "Files/CostExports/CostExports/Finopsdaily/finops-amortized-cost/20260701-20260731/5033cf31-ff03-4530-83f2-1fce8e730869/*.csv.gz"

# Explicit ABFS path to your Silver Lakehouse 'Files' and 'Tables' directories
SILVER_ABFS_FILES = "abfss://e3bf5bc5-4896-4874-a9a1-86628856bc54@onelake.dfs.fabric.microsoft.com/038d934f-db99-44f1-bd39-da7a7f68f078/Files"
SILVER_ABFS_TABLES = "abfss://e3bf5bc5-4896-4874-a9a1-86628856bc54@onelake.dfs.fabric.microsoft.com/038d934f-db99-44f1-bd39-da7a7f68f078/Tables"

STAGING_CSV_FILES_PATH = f"{SILVER_ABFS_FILES}/silver_staged_csv/amortized_cost"
TARGET_TABLE_LOCATION = f"{SILVER_ABFS_TABLES}/dbo/silver_amortized_cost"
TARGET_TABLE_NAME = "dbo.silver_amortized_cost"

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

BRONZE_CSV_PATH = "Files/CostExports/CostExports/Finopsdaily/finops-amortized-cost/20260701-20260731/5033cf31-ff03-4530-83f2-1fce8e730869/*.csv.gz"

# Explicit ABFS path to your Silver Lakehouse 'Files' and 'Tables' directories
SILVER_ABFS_FILES = "abfss://e3bf5bc5-4896-4874-a9a1-86628856bc54@onelake.dfs.fabric.microsoft.com/038d934f-db99-44f1-bd39-da7a7f68f078/Files"
SILVER_ABFS_TABLES = "abfss://e3bf5bc5-4896-4874-a9a1-86628856bc54@onelake.dfs.fabric.microsoft.com/038d934f-db99-44f1-bd39-da7a7f68f078/Tables"

STAGING_CSV_FILES_PATH = f"{SILVER_ABFS_FILES}/silver_staged_csv/amortized_cost"
TARGET_TABLE_LOCATION = f"{SILVER_ABFS_TABLES}/dbo/silver_amortized_cost"
TARGET_TABLE_NAME = "dbo.silver_amortized_cost"

print(f"Reading CSV from: {BRONZE_CSV_PATH}")

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
