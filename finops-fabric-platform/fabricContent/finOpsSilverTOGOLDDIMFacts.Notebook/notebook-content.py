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
# META         }
# META       ]
# META     },
# META     "warehouse": {
# META       "default_warehouse": "33ad4905-e22b-a73b-4423-2f848bc53753",
# META       "known_warehouses": [
# META         {
# META           "id": "33ad4905-e22b-a73b-4423-2f848bc53753",
# META           "type": "Datawarehouse"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# ==========================================
# 1. IMPORTS & SETUP
# ==========================================
from pyspark.sql.functions import col, row_number, lit, coalesce, to_date, year, quarter, month, date_format,  get_json_object, row_number
from pyspark.sql.window import Window
import com.microsoft.spark.fabric
from com.microsoft.spark.fabric.Constants import Constants



SILVER_TABLE = "dbo.silver_amortized_cost"
WAREHOUSE_NAME = "Gold"

print(f"Reading Silver table: {SILVER_TABLE}")
df_silver = spark.table(SILVER_TABLE)
df_silver.head(10)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# dim dat


df_dates = df_silver.filter(col("usagedate").isNotNull()).select(col("usagedate").alias("fullDate")).distinct()

dim_date = (
    df_dates
    .withColumn("date_key", date_format(col("fullDate"), "yyyyMMdd").cast("int"))
    .withColumn("dayOfWeek", date_format(col("fullDate"), "EEEE"))
    .withColumn("monthName", date_format(col("fullDate"), "MMMM"))
    .withColumn("quarter", quarter(col("fullDate")))
    .withColumn("fiscalYear", year(col("fullDate")))
    .withColumn("billingMonth", date_format(col("fullDate"), "MM").cast("int"))
)

# 2. Filter out date keys that already exist in the warehouse to prevent duplicates
try:
    existing_dim_date = spark.read.synapsesql(f"{WAREHOUSE_NAME}.dbo.dimDate")
    
    # Keep only rows where the date_key does not already exist in the target table
    dim_date_new = dim_date.join(
        existing_dim_date,
        dim_date.date_key == existing_dim_date.date_key,
        "left_anti"
    )
except Exception:
    # If the table doesn't exist yet (first-time execution), write the full dataset
    dim_date_new = dim_date

# 3. Safely append only the new, unique records using the native Fabric synapsesql write method
dim_date_new.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimDate")
print("Successfully pushed 'dbo.dimDate' to Gold Warehouse without duplicates!")
#we would like to increment instead of overwrite.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 3. BUILD & WRITE DIM RESOURCE
# ==========================================
# 1. Build your dim_resource dataframe using your exact logic
df_resources = (
    df_silver
    .filter(col("resourceid").isNotNull())
    .select(
        col("resourceid"),
        col("resourcegroupname").alias("resourcename"),  # Use resourcegroupname instead
        col("consumedservice").alias("resourceType"),
        col("resourcelocation").alias("region"),
        col("publishername").alias("provider")
    )
    .dropDuplicates(["resourceid"])
)

window_res = Window.orderBy("resourceid")
dim_resource = df_resources.withColumn("resourceKey", row_number().over(window_res))

# 2. Filter out resource IDs that already exist in the warehouse to prevent duplicates
try:
    existing_dim_resource = spark.read.synapsesql(f"{WAREHOUSE_NAME}.dbo.dimResource")
    
    # Keep only rows where the resourceid does not already exist in the target table
    dim_resource_new = dim_resource.join(
        existing_dim_resource,
        dim_resource.resourceid == existing_dim_resource.resourceid,
        "left_anti"
    )
except Exception:
    # If the table doesn't exist yet (first-time execution), write the full dataset
    dim_resource_new = dim_resource

# 3. Safely append only the new, unique records
dim_resource_new.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimResource")
print("Successfully pushed 'dbo.dimResource' to Gold Warehouse without duplicates!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 4. BUILD & WRITE DIM COST CENTER
# ==========================================

df_costcenters = (
    df_silver
    .filter(col("costcentercode").isNotNull())
    .select(
        col("costcentercode"),
        col("servicefamily").alias("department"),
        lit("Default Business Unit").alias("businessUnit"),
        lit(None).cast("string").alias("ownerEmail"),
        lit(None).cast("string").alias("budgetCode")
    )
    .dropDuplicates(["costcentercode"])
)

window_cc = Window.orderBy("costcentercode")
dim_costcenter = df_costcenters.withColumn("costCenterKey", row_number().over(window_cc))


try:
    existing_dim_costcenter = spark.read.synapsesql(f"{WAREHOUSE_NAME}.dbo.dimCostCenter")
    
    
    dim_costcenter_new = dim_costcenter.join(
        existing_dim_costcenter,
        dim_costcenter.costcentercode == existing_dim_costcenter.costcentercode,
        "left_anti"
    )
except Exception:
    # If the table doesn't exist yet (first-time execution), write the full dataset
    dim_costcenter_new = dim_costcenter

# 3. Safely append only the new, unique records
dim_costcenter_new.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimCostCenter")
print("Successfully pushed 'dbo.dimCostCenter' to Gold Warehouse without duplicates!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 5. BUILD & WRITE DIM TAGS
# ==========================================
from pyspark.sql.functions import col, lit, get_json_object, row_number
from pyspark.sql.window import Window

# 1. Build incoming tags dataframe
df_tags = (
    df_silver
    .select(
        get_json_object(col("tags"), "$.environment").alias("environmentTag"),
        get_json_object(col("tags"), "$.project").alias("applicationTag"),
        lit(None).cast("string").alias("complianceTag"),
        get_json_object(col("tags"), "$.owner").alias("costOwnerTag"),
        col("taghash")
    )
    .dropDuplicates(["taghash"])
)

# 2. Read existing dimension table from the warehouse (if it already exists)
try:
    existing_dim_tags = spark.read.synapsesql(f"{WAREHOUSE_NAME}.dbo.dimTags")
    
    # Keep only incoming tags that do NOT already exist in the warehouse based on taghash
    df_tags_new = df_tags.join(
        existing_dim_tags,
        df_tags.taghash == existing_dim_tags.taghash,
        "left_anti"
    )
except Exception:
    # If the table doesn't exist yet (first-time run), process all incoming rows
    df_tags_new = df_tags

# 3. Generate surrogate key only for the brand-new rows
window_tags = Window.orderBy("taghash")
dim_tags = df_tags_new.withColumn("tagKey", row_number().over(window_tags))

# 4. Append safely
dim_tags.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimTags")
print("Successfully pushed new records to 'dbo.dimTags' in Gold Warehouse!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 6. BUILD & WRITE DIM COMMITMENT DISCOUNT
# ==========================================

df_commitments = (
    df_silver
    .filter(col("commitmentid").isNotNull())
    .select(
        col("commitmentid").alias("CommitmentId"),
        col("pricingmodel").alias("CommitmentType"),
        col("term"),
        lit("Monthly").alias("PaymentOption"),
        lit(None).cast("date").alias("ExpirationDate")
    )
    .dropDuplicates(["CommitmentId"])
)

window_comm = Window.orderBy("CommitmentId")
dim_commitment = df_commitments.withColumn("CommitmentKey", row_number().over(window_comm))

# 2. Filter out commitment IDs that already exist in the warehouse to prevent duplicates
try:
    existing_dim_commitment = spark.read.synapsesql(f"{WAREHOUSE_NAME}.dbo.dimCommitmentDiscount")
    
    # Keep only rows where the CommitmentId does not already exist in the target table
    dim_commitment_new = dim_commitment.join(
        existing_dim_commitment,
        dim_commitment.CommitmentId == existing_dim_commitment.CommitmentId,
        "left_anti"
    )
except Exception:
    # If the table doesn't exist yet (first-time execution), write the full dataset
    dim_commitment_new = dim_commitment

# 3. Safely append only the new, unique records
dim_commitment_new.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimCommitmentDiscount")
print("Successfully pushed 'dbo.dimCommitmentDiscount' to Gold Warehouse without duplicates!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 2. BUILD & WRITE FACT COST
# ==========================================
from pyspark.sql.functions import col, lit, row_number, current_timestamp, date_format
from pyspark.sql.window import Window
from pyspark.sql.types import TimestampType

# 1. Join Silver back to Dimensions to pick up surrogate keys
df_fact_stg = (
    df_silver
    .join(dim_resource, "resourceid", "left")
    .join(dim_costcenter, "costcentercode", "left")
    .join(dim_tags, "taghash", "left")
    .join(dim_commitment, df_silver["commitmentid"] == dim_commitment["CommitmentId"], "left")
)

fact_cost = (
    df_fact_stg
    .withColumn("dateKey", date_format(col("usagedate"), "yyyyMMdd").cast("int"))
    .select(
        col("dateKey"),
        col("resourceKey"),
        col("costCenterKey"),
        col("tagKey"),
        col("CommitmentKey").alias("commitmentKey"),
        col("chargetype"),
        col("pricingmodel"),
        col("billedcost").alias("billedCost"),
        col("effectivecost").alias("effectiveCost"),
        col("paygcost").alias("listCost"),
        col("usagequantity").alias("usageQuantity"),
        col("unitofmeasure").alias("usageUnit")
    )
)

# 2. Add and cast insert_datetimestamp column to match Warehouse TimestampType
fact_cost_with_ts = fact_cost.withColumn("insert_datetimestamp", current_timestamp().cast(TimestampType()))

# 3. Generate fact primary key (costFactKey)
window_fact = Window.orderBy(lit(1))
fact_cost_final = fact_cost_with_ts.withColumn("costFactKey", row_number().over(window_fact).cast("bigint"))

# 4. Reject incoming rows if their dateKey already exists in the table
try:
    existing_fact = spark.read.synapsesql(f"{WAREHOUSE_NAME}.dbo.factCost")
    
    # Left anti join on dateKey to reject/drop data if the date already exists
    fact_cost_filtered = fact_cost_final.join(
        existing_fact.select("dateKey").distinct(),
        "dateKey",
        "left_anti"
    )
except Exception:
    fact_cost_filtered = fact_cost_final

# 5. Write Fact Table to Warehouse using native Fabric connector
fact_cost_filtered.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.factCost")
print("Successfully pushed filtered 'dbo.factCost' to Gold Warehouse!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
