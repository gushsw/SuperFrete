import boto3 as b3
import pendulum as pdl
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.sensors.glue_crawler import GlueCrawlerSensor
from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from airflow.utils.trigger_rule import TriggerRule

# Configurações da DAG
DAG_ID = 'ETL_glue_SF_Bronze_Silver_Gold'
ROLE_ARN_KEY = "ROLE_ARN"  # Deve ser configurado com o ARN da role IAM correta

# Dados de Exemplo
EX_DATA = """Frete1, 120,20km,0\nFrete2, 135,35km,1\nFrete3, 140,40km,0\n"""

EX_SCRIPT_BRONZE = """
from pyspark.context import SparkContext
from awsglue.context import GlueContext

glueContext = GlueContext(SparkContext.getOrCreate())
datasource = glueContext.create_dynamic_frame.from_catalog(
    database='{db_name}', table_name='input')

datasource.toDF().write.format('parquet').mode("append").save('{output_path}')
"""

EX_SCRIPT_SILVER = """
from pyspark.context import SparkContext
from awsglue.context import GlueContext

glueContext = GlueContext(SparkContext.getOrCreate())
datasource = glueContext.create_dynamic_frame.from_catalog(
    database='{db_name}', table_name='bronze')

# Aplicar algumas transformações nos dados para a camada Silver
transformed_data = datasource.toDF().filter(datasource["Frete"] > 130)

transformed_data.write.format('parquet').mode("append").save('{output_path}')
"""

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

# Definindo a DAG
with DAG(
    dag_id=DAG_ID,
    schedule_interval="@once",
    start_date=pdl.datetime(2024, 8, 19),
    tags=["ETL_SuperFrete"],
    catchup=False,
) as dag:
    
    role_arn = "arn:aws:iam::123456789012:role/MyGlueRole"  # Substitua pelo seu ARN real
    role_name = get_role_name(role_arn)

    glue_crawler_name_bronze = "crawler_bronze"
    glue_db_name_bronze = "db_bronze"
    glue_job_name_bronze = "job_bronze"
    bucket_name_bronze = "superfrete-datalake-bronze"

    glue_crawler_name_silver = "crawler_silver"
    glue_db_name_silver = "db_silver"
    glue_job_name_silver = "job_silver"
    bucket_name_silver = "superfrete-datalake-silver"

    glue_crawler_name_gold = "crawler_gold"
    glue_db_name_gold = "db_gold"
    glue_job_name_gold = "job_gold"
    bucket_name_gold = "superfrete-datalake-gold"

    # Upload do arquivo e script para a camada Bronze
    upload_bronze_data = S3CreateObjectOperator(
        task_id="upload_bronze_data",
        s3_bucket=bucket_name_bronze,
        s3_key="input/input.parquet",
        data=EX_DATA,
        replace=True,
    )

    upload_bronze_script = S3CreateObjectOperator(
        task_id="upload_bronze_script",
        s3_bucket=bucket_name_bronze,
        s3_key="bronze_script.py",
        data=EX_SCRIPT_BRONZE.format(db_name=glue_db_name_bronze, output_path=f"s3://{bucket_name_bronze}/output"),
        replace=True,
    )

    # Glue tasks para Bronze, Silver e Gold
    submit_bronze_glue_job = GlueJobOperator(
        task_id="submit_bronze_glue_job",
        job_name=glue_job_name_bronze,
        script_location=f"s3://{bucket_name_bronze}/bronze_script.py",
        s3_bucket=bucket_name_bronze,
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    crawl_silver = GlueCrawlerSensor(
        task_id="crawl_silver",
        crawler_name=glue_crawler_name_silver,
    )

    submit_silver_glue_job = GlueJobOperator(
        task_id="submit_silver_glue_job",
        job_name=glue_job_name_silver,
        script_location=f"s3://{bucket_name_silver}/silver_script.py",
        s3_bucket=bucket_name_silver,
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    crawl_gold = GlueCrawlerSensor(
        task_id="crawl_gold",
        crawler_name=glue_crawler_name_gold,
    )

    submit_gold_glue_job = GlueJobOperator(
        task_id="submit_gold_glue_job",
        job_name=glue_job_name_gold,
        script_location=f"s3://{bucket_name_gold}/gold_script.py",
        s3_bucket=bucket_name_gold,
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    # Encadeamento das tarefas
    (
        upload_bronze_data
        >> upload_bronze_script
        >> submit_bronze_glue_job
        >> crawl_silver
        >> submit_silver_glue_job
        >> crawl_gold
        >> submit_gold_glue_job
    )
