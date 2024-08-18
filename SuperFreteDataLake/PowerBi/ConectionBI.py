import boto3
import pandas as pd
import datetime
import pyarrow as pa
from io import BytesIO

bucket_name = 'superfrete-datalake-gold'
folder_name = 'negócio1/'
file_name = 'fretesRJ.parquet' # Ajusta a formatação do nome do arquivo
key = folder_name + file_name


# Cria uma sessão do S3
s3 = boto3.client('s3', region_name='us-east-1')

# Lê o arquivo Parquet do S3
obj = s3.get_object(Bucket=bucket_name, Key=key)
data = obj['Body'].read()

# Usa BytesIO para ler o arquivo Parquet
buffer = BytesIO(data)
df = pd.read_parquet(buffer)

# Exibe o DataFrame
print(df)
