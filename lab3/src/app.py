from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

from src import etl_pipeline, ml_pipeline


def main():
    
    spark = SparkSession.builder \
        .appName("EtlPipeline") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        
    spark = configure_spark_with_delta_pip(spark).getOrCreate()

    etl_pipeline.loader(
        spark=spark,
        origin_path="/app/data/raw_dataset.csv", 
    )
    
    ml_pipeline.run_training(spark)
    spark.stop()


if __name__ == "__main__":
    main()