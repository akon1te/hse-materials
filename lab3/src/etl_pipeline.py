from pyspark.sql import SparkSession

import logging


def loader(
    spark: SparkSession,
    origin_path: str,
):
    logger = logging.getLogger("py4j")
    logger.setLevel(logging.ERROR)
    
    # reading raw dataset (bronze layer)
    raw_dataset = spark.read.csv(origin_path, header=True, inferSchema=True) 
    raw_dataset.show(5)
    raw_dataset.write.format("delta") \
        .mode("overwrite") \
        .save("/app/data/bronze/raw_dataset")
    
    # processing raw dataset (silver layer)
    silver_df = (
        spark.read.format("delta").load("/app/data/bronze/raw_dataset")
        .repartition(spark.sparkContext.defaultParallelism)
        .dropna(subset=["Strikeouts", "Hits", "Doubles", "Triples", "Home_runs"])
        .withColumnRenamed("Hall_of_Fame", "label")
        .drop("Number_seasons", "Hall_of_Fame")
    )
        
    silver_df.write.format("delta") \
        .mode("overwrite") \
        .option("delta.autoOptimize.optimizeWrite", "true") \
        .save("/app/data/silver/processed_dataset")
        
    # aggregating silver table (gold layer)
    gold_df = (
        spark.read.format("delta").load("/app/data/silver/processed_dataset")
    )
    
    gold_df.repartition(spark.sparkContext.defaultParallelism) \
        .write.format("delta") \
        .mode("overwrite") \
        .option("delta.autoOptimize.optimizeWrite", "true") \
        .save("/app/data/gold/prepared_dataset")
