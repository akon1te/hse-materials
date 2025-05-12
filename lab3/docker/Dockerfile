FROM bitnami/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir delta-spark==3.2.0 pyspark mlflow pandas numpy xgboost

# Add PySpark to PATH for the spark user
ENV PATH=$PATH:/home/spark/.local/bin

RUN export JAVA_HOME=/opt/java/openjdk
RUN export PYSPARK_PYTHON=$(which python3)
RUN export SPARK_VERSION=3.5

RUN mkdir -p /opt/spark/conf

COPY log4j.properties /opt/spark/conf/log4j.properties

ENV SPARK_CONF_DIR=/opt/spark/conf

RUN mkdir -p /app/src /app/data /app/notebooks /app/logs
WORKDIR /app