import boto3 as b3
import pendulum as pdl
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.providers.amazon.aws.sensors.glue_crawler import GlueCrawlerSensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

# Configurações da DAG
DAG_ID = 'silver_to_gold_SF'
ROLE_ARN_KEY = "ROLE_ARN"

EX_SCRIPT_GOLD = """
from pyspark.context import SparkContext
from awsglue.context import GlueContext

glueContext = GlueContext(SparkContext.getOrCreate())
datasource = glueContext.create_dynamic_frame.from_catalog(
    database='{db_name}', table_name='silver')

# Aplicar mais transformações para a camada Gold
final_data = datasource.toDF().groupBy("Frete").agg({"Distancia": "max"})

final_data.write.format('parquet').mode("append").save('{output_path}')
"""

@task
def get_role_name(arn: str) -> str:
    return arn.split("/")[-1]

with DAG(
    dag_id=DAG_ID,
    schedule_interval="@once",
    start_date=pdl.datetime(2024, 8, 19),
    tags=["Exemplo_SuperFrete"],
    catchup=False,
) as dag:
    
    role_name = get_role_name('{{ var.value.ROLE_ARN }}')

    glue_crawler_config = {
        "Name": "silver_crawler",
        "Role": "{{ var.value.ROLE_ARN }}",
        "DatabaseName": "silver_db",
        "Targets": {"S3Targets": [{"Path": "s3://superfrete-datalake-silver/input"}]}
    }

    crawl_silver = GlueCrawlerSensor(
        task_id="crawl_silver",
        crawler_name="silver_crawler",
        config=glue_crawler_config,
    )

    move_to_gold = GlueJobOperator(
        task_id="move_to_gold",
        job_name="move_silver_to_gold",
        script_location="s3://superfrete-datalake-silver/etl_script.py",
        s3_bucket="superfrete-datalake-silver",
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    crawl_silver >> move_to_gold
