# DataLake SuperFrete
Os arquivos deste repositório têm como objetivo implementar uma arquitetura de dados em um DataLake AWS, projetada para suportar um ambiente de Big Data, sendo esta arquitetura capaz de lidar com:

  1) Processamento de dados em larga escala;
  2) Atualizações diárias em batches de dados;
  3) Alta disponibilidade de dados para análise.
     
Esses pontos são possíveis através de pipelines orquestrados com Apache Airflow.

# Arquitetura
Com o objetivo de garantir uma arquitetura simples e otimizada, evitando custos desnecessários, considerando que estamos lidando com um ambiente em nuvem e que serviços desnecessários e mal otimizados podem resultar em custos elevados ao longo do projeto, o que pode comprometer a implementação do DataLake e até mesmo da cultura data-driven. Considerando esses motivos, esta arquitetura consiste no uso dos seguintes serviços AWS:

# Desenho da arquitetura: 
![image](https://github.com/user-attachments/assets/a14bd37f-8eb9-40bd-8d2c-7fd227cade5a)

  1) S3 Buckets: Comumente conhecido como S3 uma sigla para "Simple Storage Service", é um serviço de armazenamento de dados da AWS que se assemelha a um file server, mas com a peculiaridade de ser um serviço serverless. Sendo assim, os buckets S3 são utilizados nesta arquitetura para constituir as três camadas do DataLake da SuperFrete, seguindo a estrutura de medalhão: superfrete-bucket-bronze, superfrete-bucket-silver, superfrete-bucket-gold. Além disso, haverá mais um bucket, que auxiliará como repositório do time e servirá para a configuração do MWAA (Managed Workflows for Apache Airflow)¹.
  ¹O serviço MWAA será explicado mais à frente.

  2) Glue: O Glue é um serviço da AWS onde podemos criar jobs ETL, visualizar dados em uma camada, monitorar todo o processo ETL e catalogar dados. Nesta arquitetura, o Glue será utilizado para executar pipelines ETL, que serão orquestrados pelo Apache Airflow, sendo todo o poder de processamento necessário para suportar o ETL de batches diários de dados fornecido por máquinas virtuais do tipo G1X, G2X, G4X, G8X, que variam de 4 CPUs e 16 GB de RAM até 32 CPUs e 128 GB de RAM. Isso é significativamente mais econômico e simples do que se tivéssemos escolhido utilizar máquinas virtuais no serviço EC2 (Elastic Cloud Computing) da AWS.

# Configurando o ambiente
Para construir o DataLake dentro da AWS, você deverá instalar os seguintes pré-requisitos:

1) Instalar o Python em uma versão igual ou superior à 3.11: https://www.python.org/downloads/
2) Instalar AWS CLI, seguindo o passo a passo de acordo com o seu sistema operacional: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
   
ATENÇÃO!
 - Caso o seu ambiente possua validação de usuários federados via AD, você deverá configurar os usuários seguindo as instruções neste link: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html.
Após a instalação do AWS CLI, não esqueça de configurar os seus parâmetros de usuário através do comando aws configure, fornecendo suas chaves de acesso. Esse procedimento evita a necessidade de passar suas chaves de acesso como constantes dentro dos códigos Python de implementação do ambiente. Instruções neste link: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html.

Após a instalação do Python, você deverá instalar as seguintes bibliotecas Python:
Considere criar um ambiente virtual para evitar conflito de dependências!!!

1) boto3: pip install boto3 ou python -m pip install boto3
Explicação: biblioteca Python que nada mais é quem um SDK da AWS, simples assim!
Documentação: **https://pypi.org/project/boto3/**

2) logging: pip install logging ou python -m pip install logging
Explicação: biblioteca Python utilizada para alertar falhas de login no ambiente.
Documentação: **https://pypi.org/project/logging2/**

3) json: pip install json ou python -m pip install json
Explicação: biblioteca Python utilizada para passar os parâmetros de acesso dos usuários e definição dos grupos dentro da AWS utilizando JSON.
Documentação: **https://pypi.org/project/JSON4JSON/**

4) pendulum: pip install pendulum ou python -m pip install pendulum
Explicação: biblioteca Python utiulizada para construir constantes temporais com day, week, timezone e etc! Sendo um grande facilitador para criar triggers de execução dentro da amazon pelo airflow.
Documentação: **https://pypi.org/project/pendulum/**
