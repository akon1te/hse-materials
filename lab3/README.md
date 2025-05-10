# Lab2 Hadoop + Spark
Мяков Тимофей ИАД24

## Getting start
### 1 DataNode
```bash
docker-compose -f docker-compose-1node.yml up -d
```
### 3 DataNode
```bash
docker-compose -f docker-compose-3node.yml up -d
```


## Dataset
```bash
docker cp data/salaries.csv namenode:/
docker cp -L src/. spark-master:/opt/bitnami/spark/

docker exec -it namenode bash
hdfs dfs -put salaries.csv /
exit
```


## Experiments

### 1 DataNodes

```bash
docker exec -it spark-master spark-submit --master spark://spark-master:7077 spark_app.py -pth hdfs://namenode:9000/salaries.csv -n 1

docker cp spark-master:/opt/bitnami/spark/app_metrics_1nodes.png images
```

![](./images/app_metrics_1nodes.png)

### 3 DataNodes

For general run use the following command
```bash
docker exec -it spark-master spark-submit --master spark://spark-master:7077 spark_app.py -pth hdfs://namenode:9000/salaries.csv -n 3

docker cp spark-master:/opt/bitnami/spark/app_metrics_3nodes.png images
```

![](./images/app_metrics_3nodes.png)


## 
### 1 DataNodes
```bash
docker-compose -f docker-compose-1node.yml down
```

### 3 DataNodes
```bash
docker-compose -f docker-compose-3node.yml down
```