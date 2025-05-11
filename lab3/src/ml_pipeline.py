import mlflow

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def prepare_pipeline(df):
    
    feature_columns = [col for col in df.columns if col not in ['label', 'Position']]
    feature_columns.append("position_vec")
    print(f'Feature columns {feature_columns}')
            
    model_params = {
        "numTrees": 10,
        "maxDepth": 5,
        "featuresCol": "features",
        "labelCol": "label",
        "seed": 54,
    }
    print(f'Boosting params {model_params}')
    
    pos_indexer = StringIndexer(inputCol="Position", outputCol="position_indexed")
    encoder = OneHotEncoder(inputCol="position_indexed", outputCol="position_vec")
    assembler = VectorAssembler(
        inputCols=feature_columns,
        outputCol="features"
    )
    model = RandomForestClassifier(**model_params)
    pipeline = Pipeline(
        stages=[pos_indexer, encoder, assembler, model]
    )
    
    return pipeline, model_params
    

def get_metrics(preds):

    acc = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName="accuracy"
    ).evaluate(preds)
    
    f1 = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName="f1"
    ).evaluate(preds)
    
    return {
        "acc": acc,
        "f1": f1
    }


def run_training(spark: SparkSession):

    df = spark.read.format("delta").load("/app/data/gold/prepared_dataset")
    train_data, val_data = df.randomSplit([0.8, 0.2], seed=42)
    
    pipeline, model_params = prepare_pipeline(df)
    
    
    mlflow.set_tracking_uri("http://0.0.0.0:8000")
    
    if not mlflow.get_experiment_by_name("MyClfModel"):
        mlflow.create_experiment("MyClfModel")
    mlflow.set_experiment("MyClfModel")

    print('Start pipeline training')
    with mlflow.start_run():
        mlflow.log_params(model_params)
    
        model = pipeline.fit(train_data)

        mlflow.spark.log_model(model, "base-tree-model")
        mlflow.log_artifact("/app/logs/pipe.log")
        
        val_preds = model.transform(val_data)
        metrics = get_metrics(val_preds)
        
        mlflow.log_metrics(metrics)
        print(f"Metrics: {metrics}")
