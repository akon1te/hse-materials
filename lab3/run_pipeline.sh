#!/bin/bash

mkdir -p data/{bronze,silver,gold} 

docker-compose build
docker-compose up -d

docker exec -t spark spark-submit --packages io.delta:delta-spark_2.12:3.2.0 \
 --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/opt/spark/conf/log4j.properties" \
 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
 --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"  etl_pipeline.py

 docker exec -t spark spark-submit --packages io.delta:delta-spark_2.12:3.2.0 \
 --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/opt/spark/conf/log4j.properties" \
 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
 --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"  ml_pipeline.py

 mlflow ui --port 8060