from pyspark.sql import SparkSession


def loader(
    spark: SparkSession,
    origin_path: str,
):
    # Bronze layer (читаем сырые данные)
    raw_dataset = spark.read.csv(origin_path, header=True, inferSchema=True) 
    raw_dataset.show(5)
    raw_dataset.repartition(spark.sparkContext.defaultParallelism) \
        .write.format("delta") \
        .mode("overwrite") \
        .save("/app/data/bronze/raw_dataset")
    
    # Silver layer (чистим данные)
    silver_df = (
        spark.read.format("delta").load("/app/data/bronze/raw_dataset")
        .repartition(spark.sparkContext.defaultParallelism)
        .dropna(subset=["Strikeouts", "Hits", "Doubles", "Triples", "Home_runs"])
        .withColumnRenamed("Hall_of_Fame", "label")
        .drop("Number_seasons", "Hall_of_Fame")
    )
    silver_df.show(5)
        
    silver_df.repartition(spark.sparkContext.defaultParallelism) \
        .write.format("delta") \
        .mode("overwrite") \
        .option("delta.autoOptimize.optimizeWrite", "true") \
        .save("/app/data/silver/processed_dataset")
        
    # Gold layer (аггрегируем данные)
    silver_df = spark.read.format("delta").load("/app/data/silver/processed_dataset")
    
    gold_df = (
       silver_df.withColumn('AvgHist', (silver_df['Hits'] / silver_df['Games_played']))
       .withColumn('AvgStrikeouts', (silver_df['Strikeouts'] / silver_df['Games_played']))
       .withColumn('AvgDoubles', (silver_df['Doubles'] / silver_df['Games_played']))
       .withColumn('AvgTriples', (silver_df['Triples'] / silver_df['Games_played']))
       .withColumn('AvgHome_runs', (silver_df['Home_runs'] / silver_df['Games_played']))
       .withColumn('AvgWalks', (silver_df['Walks'] / silver_df['Games_played']))
       .withColumn('AvgAt_bats', (silver_df['At_bats'] / silver_df['Games_played']))
       .drop('Hits', 'Strikeouts', 'Doubles', 'Triples', 'Walks', 'Home_runs', 'At_bats')
    )
    gold_df.show(5)
    
    gold_df.repartition(spark.sparkContext.defaultParallelism) \
        .write.format("delta") \
        .mode("overwrite") \
        .option("delta.autoOptimize.optimizeWrite", "true") \
        .save("/app/data/gold/prepared_dataset")
