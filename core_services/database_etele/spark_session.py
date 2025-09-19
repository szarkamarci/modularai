from pyspark.sql import SparkSession


class MySparkSession():

    __init__(self, config_obj: dict):

        self.APP_NAME = config_obj['APP_NAME']

        #self.SUPABASE_URL = config_obj['SUPABASE_URL']
        #self.DATABASE_URL = config_obj['DATABASE_URL']
        self.JDBC_URL = config_obj['JDBC_URL']
        #self.SUPABASE_ANON_KEY = config_obj['SUPABASE_ANON_KEY']
        #self.SUPABASE_SERVICE_KEY = config_obj['SUPABASE_SERVICE_KEY']

        self.SPARK_JAR = config_obj['SPARK_JAR']
        self.USER = config_obj['USER']
        self.PASSWORD = config_obj['PASSWORD']
        self.DRIVER = config_obj['DRIVER']

        self.connection_options = {
            "url": self.JDBC_URL,
            "user": self.USER,
            "password": self.PASSWORD,
            "driver": self.DRIVER
        }

        self.spark = (
            SparkSession.builder
            .appName(self.APP_NAME)
            .config("spark.jars", self.SPARK_JAR)
            .getOrCreate()
        )

    def read_table(self,
                   config_obj: dict = None, 
                   return_spark = False, 
                   print_info = False):
    
        if config_obj == None:
            raise Exception("Missing 'config_obj'")

        
        read_text = config_obj['command_text']

        if print_info:
            print(f"Running query: {read_text}")

        df_spark = self.spark.read
                             .format("jdbc")
                             .options(**self.connection_options)
                             .option("dbtable", f"({read_text}) as t")
                             .load()

        if return_spark:
            return df_spark
        else:
            return df_spark.toPandas()
        
        return True
    
    def write_table(self,
                    config_obj: dict = None, 
                    df
                    is_spark = False, 
                    print_info = False):

        if config_obj == None:
            raise Exception("Missing 'config_obj'")
        
        write_text = config_obj['command_text']

        if print_info:
            print(f"Running query: {write_text}")

        if is_spark:
            df_spark = df
        else:
            df_spark = self.spark.createDataFrame(df)

        df_spark.write.format("jdbc")
                      .options(**self.connection_options)
                      .option("dbtable", f"({write_text}) as t")
                      .save()
                      
         return True

    def save_table(self, table_name: str, df, is_spark: bool = False, print_info: bool = False):
        if not table_name:
            raise Exception("Missing 'table_name'")
        if df is None:
            raise Exception("Missing 'df'")

        # Drop empty columns (all nulls)
        if not is_spark:
            se_ratio = (df.isnull().sum() / len(df))
            df = df[se_ratio[se_ratio < 1].index.values]

        if is_spark:
            df_spark = df
        else:
            df_spark = self.spark.createDataFrame(df)

        if print_info:
            print(f"Saving table: {table_name}, columns: {df_spark.columns}")

        df_spark.write.saveAsTable(table_name)

        return True

    def overwrite_table(self, table_name: str, df, is_spark: bool = False, print_info: bool = False):
        if not table_name:
            raise Exception("Missing 'table_name'")
        if df is None:
            raise Exception("Missing 'df'")

        df_spark = df if is_spark else self.spark.createDataFrame(df)

        if print_info:
            print(f"Overwriting table: {table_name}")

        df_spark.write.mode("overwrite").option("mergeSchema", "true").saveAsTable(table_name)
        return True

    def append_to_table(self, table_path: str, df, column_partitionby: str = None, is_spark: bool = False, print_info: bool = False):
        if not table_path:
            raise Exception("Missing 'table_path'")
        if df is None:
            raise Exception("Missing 'df'")

        df_spark = df if is_spark else self.spark.createDataFrame(df)

        if print_info:
            print(f"Appending to table: {table_path}")

        writer = df_spark.write.mode("append").format("parquet")
        if column_partitionby:
            writer = writer.partitionBy(column_partitionby)

        writer.save(table_path)
        return True

    def enable_vectorization(self, table_name: str, print_info: bool = False):
        if not table_name:
            raise Exception("Missing 'table_name'")

        if print_info:
            print(f"Altering table for vectorization: {table_name}")

        self.spark.sql(
            f"ALTER TABLE {table_name} "
            f"SET TBLPROPERTIES (delta.enableChangeDataFeed = true)"
        )
        return True