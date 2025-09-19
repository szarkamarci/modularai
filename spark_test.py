import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession   # <--- THIS LINE WAS MISSING

# -------------------------------
# 1. Load environment variables
# -------------------------------
load_dotenv()

# Build proper JDBC URL (Supabase local Postgres)
jdbc_url = "jdbc:postgresql://localhost:54322/postgres"

# Properties = credentials + driver
properties = {
    "user": "postgres",             # Supabase local default user
    "password": "postgres",         # Supabase local default password
    "driver": "org.postgresql.Driver"
}

# -------------------------------
# 2. Start Spark session
# -------------------------------
spark = (
    SparkSession.builder
    .appName("SupabaseSparkTest")
    .config("spark.jars", os.path.expanduser("~/jars/postgresql-42.7.3.jar"))
    .getOrCreate()
)

# -------------------------------
# 3. Test query: read from pg_catalog
# -------------------------------
df = spark.read.jdbc(
    url=jdbc_url,
    table="pg_catalog.pg_tables",  # system table → always exists
    properties=properties
)

print("✅ Connected to Supabase Postgres! Sample tables:")
df.select("schemaname", "tablename").show(10, truncate=False)
