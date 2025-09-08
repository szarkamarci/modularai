import pandas as pd

from pyspark import SparkContext
from pyspark.sql import SparkSession

def create_table(spark: SparkSession = None, 
                 command_obj: dict = None, 
                 print_info = False):
    
    if command_obj == None:
        raise Exception("Missing 'command_obj'")

    if print_info:
        print(f"Generate 'command_text'")
    
    command_text = command_obj['command_text']

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)

    if print_info:
        print(f"Generating table: {command_text}")
    spark.sql(command_text)
    
    return True
    
def enable_vectorization(spark: SparkSession = None, 
                         table_path: str = None, 
                         print_info = False):
    
    if table_path == None:
        raise Exception("Missing 'table_path'")

    if print_info:
        print(f"Altering table for vectorization: {table_path}")

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)
    
    spark.sql(f"ALTER TABLE {table_path} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

    return True
    
def enable_vectorization(spark: SparkSession = None, 
                         table_path: str = None, 
                         print_info = False):
    
    if table_path == None:
        raise Exception("Missing 'table_path'")

    if print_info:
        print(f"Altering table for vectorization: {table_path}")

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)
    
    spark.sql(f"ALTER TABLE {table_path} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

    return True
    
def read_table(spark: SparkSession = None, 
               query_obj: dict = None, 
               return_spark = False, 
               print_info = False):
    
    if query_obj == None:
        raise Exception("Missing 'query_obj'")

    if print_info:
        print(f"Generate 'query_text'")
    
    query_text = query_obj['query_text']

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)

    if print_info:
        print(f"Running query: {query_text}")

    df_spark = spark.sql(query_text)

    if return_spark:
        return df_spark
    else:
        return df_spark.toPandas()
    
    return True

    
def save_table(spark: SparkSession = None, 
               table_path: str = None,  
               df = None, is_spark = False, 
               print_info = False):
    
    if not table_path:
        raise Exception("Missing 'table_path'")
    elif not df:
        raise Exception("Missing 'df'")

    drop_simple_table(table_path)

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)

    se_ratio = (df.isnull().sum() / len(df))
    df = df[se_ratio[se_ratio < 1].index.values]
    
    if is_spark:
        df_spark = df
    else:
        df_spark = spark.createDataFrame(df)

    if print_info:
        print(f"Saving table: {table_path}, columns: {df.columns}")

    df_spark.write.saveAsTable(f"{table_path}")

    return True

    
def overwrite_table(spark: SparkSession = None, 
                    table_path: str = None, 
                    df = None, is_spark = False, 
                    print_info = False):
    
    if table_path == None:
        raise Exception("Missing 'table_path'")
    elif df == None:
        raise Exception("Missing 'df'")

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)

    if is_spark:
        df_spark = df
    else:
        df_spark = spark.createDataFrame(df)

    if print_info:
        print(f"Overwrite table: {table_path}")

    df_spark.write.mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{table_path}")

    return True

    
def append_to_table(spark: SparkSession = None, 
                    table_path: str = None,  
                    df = None, column_partitionby = None, is_spark = False, 
                    print_info = False):

    if table_path == None:
        raise Exception("Missing 'table_path'")
    elif df == None:
        raise Exception("Missing 'df'")

    if spark == None:
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)

    if is_spark:
        df_spark = df
    else:
        df_spark = spark.createDataFrame(df)

    if column_partitionby == None:
        df_spark.write.mode("append").format("parquet").save(f"{table_path}")
    else:
        df_spark.write.mode("append").partitionBy(column_partitionby).format("parquet").save(f"{table_path}")

    return True

    
