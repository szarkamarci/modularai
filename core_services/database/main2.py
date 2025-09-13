import os
from dotenv import load_dotenv

from pyspark import SparkContext
from pyspark.sql import SparkSession

from base_functions import create_table

load_dotenv()  # loads .env file into environment

db_url = os.getenv("DATABASE_URL")  # ex: postgresql://postgres:postgres@localhost:54322/postgres
# Convert DATABASE_URL into JDBC format
jdbc_url = db_url.replace("postgresql://", "jdbc:postgresql://")

# JDBC connection properties
properties = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

spark = (
    SparkSession.builder
    .appName("SupabaseSparkTest")
    # ⚠️ Adjust path if you saved the driver elsewhere
    .config("spark.jars", "/path/to/postgresql-42.7.3.jar")
    .getOrCreate()
)

create_table_sql = """
CREATE TABLE IF NOT EXISTS spark_test (
    id SERIAL PRIMARY KEY,
    name TEXT,
    age INT,
    city TEXT
);
"""

# Spark doesn’t execute DDL directly, so we push it via "query"
spark.read.jdbc(
    url=jdbc_url,
    table=f"({create_table_sql}) as t",
    properties=properties
)

create_table(spark = None,
             command_obj = "")
