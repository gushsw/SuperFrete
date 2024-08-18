import boto3 as b3
import pendulum as pdl
from airflow.decorators import task
from airflow.models.baseoperator import chain
from airflow.models.dag import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.hooks.glue_databrew import GlueDataBrewHook
from airflow.providers.amazon.aws.sensors.glue_crawler import GlueCrawlerSensor
from airflow.providers.amazon.aws.operators.s3 import (
    S3CreateBucketOperator,
    S3CreateObjectOperator,
    S3DeleteBucketOperator,
)
from airflow.utils.trigger_rule import TriggerRule
from tests.system.providers.amazon.aws.utils import ENV_ID_KEY, SystemTestContextBuilder, prune_logs

# Configurações da DAG
DAG_ID = 'Exemplo_glue_SF'  # SF = SuperFrete
ROLE_ARN_KEY = "ROLE_ARN"  # Deve ser configurado com o ARN da role IAM correta

# Dados e Script de Exemplo
EX_DATA = """Frete1, 120,20km,0\nFrete2, 135,35km,1\nFrete3, 140,40km,0\n"""

EX_SCRIPT = """
from pyspark.context import SparkContext
from awsglue.context import GlueContext
import boto3 as b3

glueContext = GlueContext(SparkContext.getOrCreate())

s3_client = b3.client('s3')
bucket_name = 'superfrete-datalake-dados'
scripts_folder = 'scripts/'

datasource = glueContext.create_dynamic_frame.from_catalog(
    database='{db_name}', table_name='input')

print(f'Existem {datasource.count()} itens na tabela')

output_path = f's3://{bucket_name}/output'
datasource.toDF().write.format('parquet').mode("append").save(output_path)
"""

@task
def get_role_name(arn: str) -> str:
    return arn.split("/")[-1]

@task(trigger_rule=TriggerRule.ALL_DONE)
def glue_cleanup(crawler_name: str, job_name: str, db_name: str) -> None:
    client = b3.client("glue")
    client.delete_crawler(Name=crawler_name)
    client.delete_job(JobName=job_name)
    client.delete_database(Name=db_name)

# Definindo a DAG
with DAG(
    dag_id=DAG_ID,
    schedule_interval="@once",
    start_date=pdl.datetime(2024, 8, 19),
    tags=["Exemplo_SuperFrete"],
    catchup=False,
) as dag:
    
    test_context = SystemTestContextBuilder().add_variable(ROLE_ARN_KEY).build()

    env_id = test_context[ENV_ID_KEY]
    role_arn = test_context[ROLE_ARN_KEY]
    glue_crawler_name = f"{env_id}_crawler"
    glue_db_name = f"{env_id}_glue_db"
    glue_job_name = f"{env_id}_glue_job"
    bucket_name = f"{env_id}-bucket-dados"
    role_name = get_role_name(role_arn)

    glue_crawler_config = {
        "Name": glue_crawler_name,
        "Role": role_arn,
        "DatabaseName": glue_db_name,
        "Targets": {"S3Targets": [{"Path": f"s3://{bucket_name}/input"}]}
    }

    # Tarefas do Airflow
    create_bucket = S3CreateBucketOperator(
        task_id="create_bucket",
        bucket_name=bucket_name,
    )

    upload_parquet = S3CreateObjectOperator(
        task_id="upload_parquet",
        s3_bucket=bucket_name,
        s3_key="input/input.parquet",
        data=EX_DATA,
        replace=True
    )

    upload_script = S3CreateObjectOperator(
        task_id="upload_script",
        s3_bucket=bucket_name,
        s3_key="etl_script.py",
        data=EX_SCRIPT.format(db_name=glue_db_name, bucket_name=bucket_name),
        replace=True,
    )

    crawl_s3 = GlueCrawlerSensor(
        task_id="crawl_s3",
        crawler_name=glue_crawler_name,
        config=glue_crawler_config,
    )

    wait_for_crawl = GlueCrawlerSensor(
        task_id="wait_for_crawl",
        crawler_name=glue_crawler_name,
    )

    submit_glue_job = GlueJobOperator(
        task_id="submit_glue_job",
        job_name=glue_job_name,
        script_location=f"s3://{bucket_name}/etl_script.py",
        s3_bucket=bucket_name,
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    wait_for_job = GlueCrawlerSensor(
        task_id="wait_for_job",
        crawler_name=glue_crawler_name,
    )

    delete_bucket = S3DeleteBucketOperator(
        task_id="delete_bucket",
        trigger_rule=TriggerRule.ALL_DONE,
        bucket_name=bucket_name,
        force_delete=True,
    )

    log_cleanup = prune_logs(
        [
            ("/aws-glue/crawlers", glue_crawler_name),
            ("/aws/glue/jobs/logs-v2", submit_glue_job.output),
            ("/aws/glue/jobs/error", submit_glue_job.output),
            ("/aws/glue/jobs/output", submit_glue_job.output),
        ]
    )

    # Encadeamento das tarefas
    chain(
        # Configuração inicial
        test_context,
        create_bucket,
        upload_parquet,
        upload_script,
        # Processamento de dados
        crawl_s3,
        wait_for_crawl,
        submit_glue_job,
        wait_for_job,
        # Limpeza do ambiente
        glue_cleanup(glue_crawler_name, glue_job_name, glue_db_name),
        delete_bucket,
        log_cleanup,
    )

    from tests.system.utils.watcher import watcher

    list(dag.tasks) >> watcher()
