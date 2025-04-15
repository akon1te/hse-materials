from typing import List
from argparse import ArgumentParser

import time
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, stddev, max, min

import matplotlib.pyplot as plt


logging.basicConfig(
    filename='salary_analysis.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def get_executor_memory(context):
    executor_memory_status = context._jsc.sc().getExecutorMemoryStatus()
    executor_memory_status_dict = \
        context._jvm.scala.collection.JavaConverters.mapAsJavaMapConverter(executor_memory_status).asJava()
    total_used_memory = 0
    
    for values in executor_memory_status_dict.values():
        total_memory = values._1() / (1024 * 1024)
        free_memory = values._2() / (1024 * 1024)
        used_memory = total_memory - free_memory
        total_used_memory += used_memory
    
    return total_used_memory


def analyze_metrics(app_res: List[float], opt_app_res: List[float], n_nodes: int) -> None:
    
    app_memory, app_duration = app_res
    opt_app_memory, opt_app_duration = opt_app_res
    
    plt.figure(figsize=(14, 6))

    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 5))
    ax1.bar(['no opt', 'opt'], [app_memory, opt_app_memory], width=1, edgecolor="white", linewidth=0.7);
    ax1.set_title(f'App memory (nodes={n_nodes})')

    ax2.bar(['no opt', 'opt'], [app_duration, opt_app_duration], width=1, edgecolor="white", linewidth=0.7);
    ax2.set_title(f'App time (nodes={n_nodes})');

    plt.tight_layout()
    plt.savefig(f'app_metrics_{n_nodes}nodes.png')
    logging.info(f'Metric viz dumped in app_metrics_{n_nodes}nodes.png')
    

def exp(spark: SparkSession, data_path: str, optimized=False):
    start_time = time.time()

    app_duration = []
    app_memory = []
    
    df = spark.read.csv(
        data_path,
        header=True
    )
    logging.info(f'Loaded data with {df.count()} rows from: {data_path}')
    
    filtered_df = df.filter(
        (col("employment_type") == "FT") & 
        (col("salary_in_usd").isNotNull()) &
        (col("experience_level").isNotNull())
    )

    if optimized: #оптимизация с repartition и cache
        filtered_df = filtered_df.repartition(8, "work_year", "experience_level")
        filtered_df.cache()
        _ = filtered_df.count()
    
    
    yearly_analysis = filtered_df.groupBy(
        "work_year", 
        "experience_level",
        "company_size"
    ).agg(
        avg("salary_in_usd").alias("avg_salary_usd"),
        stddev("salary_in_usd").alias("salary_stddev"),
        count("*").alias("records_count"),
        max("salary_in_usd").alias("max_salary"),
        min("salary_in_usd").alias("min_salary")
    ).orderBy("work_year", "experience_level")
    
    remote_analysis = filtered_df.groupBy(
        "remote_ratio",
        "company_size"
    ).agg(
        avg("salary_in_usd").alias("avg_salary"),
        count("*").alias("total_employees")
    ).orderBy("remote_ratio")
    
    yearly_analysis.write.mode("overwrite") \
        .csv("hdfs://namenode:9000/output/yearly_analysis")
            
    remote_analysis.write.mode("overwrite") \
        .csv("hdfs://namenode:9000/output/remote_analysis")
        
    app_memory = get_executor_memory(spark.sparkContext)
    app_duration = time.time() - start_time
        
    logging.info(f"Job user {app_memory:.4f} memory")
    logging.info(f"Job completed in {app_duration:.2f} seconds")
    
    return app_memory, app_duration


def main(data_path: str, n_nodes: int):
    
    spark = (
        SparkSession.builder
        .appName(f'SalaryAnalysis_{n_nodes}nodes')
        .config("spark.driver.memory", "10g")
        .getOrCreate()
    )
    
    app_res = exp(spark, data_path, optimized=False)
    opt_app_res = exp(spark, data_path, optimized=True)
    
    analyze_metrics(
        app_res, 
        opt_app_res, 
        n_nodes
    )
    
    spark.stop()
    

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('--data_path', '-pth')
    parser.add_argument('--n_nodes', '-n')
    args = parser.parse_args()
    
    main(args.data_path, args.n_nodes)
    