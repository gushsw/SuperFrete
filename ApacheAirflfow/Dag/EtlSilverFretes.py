import boto3 as b3
import pendulum as pdl
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.providers.amazon.aws.sensors.glue_crawler import GlueCrawlerSensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

# Configurações da DAG
DAG_ID = 'bronze_to_silver_SF'
ROLE_ARN_KEY = "ROLE_ARN"

EX_SCRIPT = """
from pyspark.context import SparkContext
from awsglue.context import GlueContext

glueContext = GlueContext(SparkContext.getOrCreate())

datasource = glueContext.create_dynamic_frame.from_catalog(
    database='{db_name}', table_name='input')

output_path = 's3://superfrete-datalake-silver/output'
datasource.toDF().write.format('parquet').mode("append").save(output_path)
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
        "Name": "bronze_crawler",
        "Role": "{{ var.value.ROLE_ARN }}",
        "DatabaseName": "bronze_db",
        "Targets": {"S3Targets": [{"Path": "s3://superfrete-datalake-bronze/input"}]}
    }

    crawl_bronze = GlueCrawlerSensor(
        task_id="crawl_bronze",
        crawler_name="bronze_crawler",
        config=glue_crawler_config,
    )

    move_to_silver = GlueJobOperator(
        task_id="move_to_silver",
        job_name="move_bronze_to_silver",
        script_location="s3://superfrete-datalake-bronze/etl_script.py",
        s3_bucket="superfrete-datalake-bronze",
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    crawl_bronze >> move_to_silver
