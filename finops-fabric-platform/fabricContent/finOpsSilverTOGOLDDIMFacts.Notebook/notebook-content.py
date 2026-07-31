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
from pyspark.sql.functions import col, row_number, lit, coalesce, to_date, year, quarter, month, date_format
from pyspark.sql.window import Window

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

# ==========================================
# 2. BUILD & WRITE DIM DATE
# ==========================================
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

dim_date.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimDate")
print("Successfully pushed 'dbo.dimDate' to Gold Warehouse!")

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

dim_resource.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimResource")
print("Successfully pushed 'dbo.dimResource' to Gold Warehouse!")

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

dim_costcenter.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimCostCenter")
print("Successfully pushed 'dbo.dimCostCenter' to Gold Warehouse!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 5. BUILD & WRITE DIM TAGS
# ==========================================
df_tags = (
    df_silver
    .select(
        col("tag_environment").alias("environmentTag"),
        col("tag_project").alias("applicationTag"),
        lit(None).cast("string").alias("complianceTag"),
        col("tag_owner").alias("costOwnerTag"),
        col("taghash")
    )
    .dropDuplicates(["taghash"])
)

window_tags = Window.orderBy("taghash")
dim_tags = df_tags.withColumn("tagKey", row_number().over(window_tags))

dim_tags.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimTags")
print("Successfully pushed 'dbo.dimTags' to Gold Warehouse!")

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

dim_commitment.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.dimCommitmentDiscount")
print("Successfully pushed 'dbo.dimCommitmentDiscount' to Gold Warehouse!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ==========================================
# 7. BUILD & WRITE FACT TABLE WITH FOREIGN KEYS
# ==========================================

# Join Silver back to Dimensions to pick up the surrogate keys
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

# Generate fact primary key (costFactKey)
window_fact = Window.orderBy(lit(1))
fact_cost_final = fact_cost.withColumn("costFactKey", row_number().over(window_fact).cast("bigint"))

# Write Fact Table to Warehouse
fact_cost_final.write.mode("append").synapsesql(f"{WAREHOUSE_NAME}.dbo.factCost")
print("Successfully pushed 'dbo.factCost' to Gold Warehouse!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
