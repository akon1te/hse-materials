# scripts/train_model.py
import mlflow
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import balanced_accuracy_score, f1_score
import matplotlib.pyplot as plt

import logging


def main():
    spark = SparkSession.builder \
        .appName("MLPipeline") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    df = spark.read.format("delta").load("/app/data/gold/prepared_dataset")

    indexer = StringIndexer(inputCol="Position", outputCol="position_indexed")
    encoder = OneHotEncoder(inputCol="position_indexed", outputCol="position_vec")
    pipeline = Pipeline(stages=[indexer, encoder])
    prepared_df = (
        pipeline.fit(df)
        .transform(df)
        .drop("Position", "position_indexed")
    )
    prepared_df.show(5)
    
    feature_columns = [col for col in prepared_df.columns if col != 'label']
    assembler = VectorAssembler(
        inputCols=feature_columns,
        outputCol="features"
    )
    prepared_features = assembler.transform(prepared_df)
    train_data = prepared_features.select("features", "label").toPandas()

    X = train_data["features"].tolist()
    y = train_data["label"].tolist()
    
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.3, random_state=42)
    print(f'Shapes X: {len(X_train)}, y: {len(y_train)}')
    print(f'Shapes X: {len(X_valid)}, y: {len(y_valid)}')
    
    mlflow.set_tracking_uri("file:/app/mlruns")

    with mlflow.start_run():
        
        boosting_params = {
            "objective": "multi:softmax",
            "m"
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 30,
            "base_score": 0.5,
            "eval_metric": ["merror", "mlogloss", 'auc']
        }
        
        model = XGBClassifier(**boosting_params)
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_valid, y_valid)],
            verbose=True
        )
        
        mlflow.log_params(boosting_params)

        y_valid_pred = model.predict(X_valid)
        valid_acc = balanced_accuracy_score(y_valid, y_valid_pred)
        valid_f1 = f1_score(y_valid, y_valid_pred, average='macro')

        mlflow.log_metrics({
            "valid_accuracy": valid_acc,
            "valid_f1": valid_f1,
        })

        evals_result = model.evals_result()        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        ax1.plot(evals_result['validation_0']['merror'], label='Valid Merror')
        ax2.plot(evals_result['validation_0']['mlogloss'], label='Valid Mlogloss')
        ax1.set_title('Classification Error')
        ax2.set_title('LogLoss Error')
        ax1.legend()
        ax1.grid()
        
        fig.savefig('full_figure.png')

if __name__ == "__main__":
    main()