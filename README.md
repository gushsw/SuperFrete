# DataLake SuperFrete
Os arquivos que estão neste repositório tem como objetivo implementar uma arquitetura de dados de datalake AWS, projetada para suportar um ambiente de big data, incluindo:
  1) processamento em larga escala, 
  2) atualização em batch's diários, 
  3) análise de dados
sendo este pontos possíveis através de um pipeline orquestrado com Apache Airflow.

# Arquitetura
Com o objetivo de garantir uma arquitetura simples e otimizada, com o objetivo de evitar custos desnecessários, pois estamos lidando com ambiente em nuvem e temos que considerar que serviços desnecessários e mal otimizados, gerenciados e otimizado, podemos nos deparar com custos elevados e desnecessários ao longo do projeto, o que pode colocar a implementação do projeto de um datalake e até mesmo da cultura datadriven em jogo. Sendo assim, ao considerar os motivos que já foram supracitados, esta arquitetura era consistir no uso dos seguinte serviços AWS:

  1) S3 BUCKET's: Comulmente conhecido como S3, sendo sigla de "simple storage service" é um serviço de armazenamento de dados da AWS que muito se assemelha a um file server, mas com a pecularidade de ser um serviço serveles. Sendo assim, os buckets S3 são utilizados nesta arquitetura para constituir as três camadas do datalake da SupreFrete, que seguirá a estrutura de medalhão, sendo elas: superfrete-bucke-bronze,superfrete-bucke-silver,superfrete-bucke-gold. Porém, também será possível encontrar mais um bucket, que auxiliará como repositório do time, assim como também servirá para configuração do MWAA(Managed Workflows for Apache Airflow)¹
     ¹O serviçço MWAA será explicado mais a frente
     
  2) Glue: O Glue é um serviço da AWS em que podemos criar jobs ETL, visualizar dados em uma camada, monitorar todo o processo ETL, catalogar dados. Porém, nesta arquitetura, o Glue servirá para executar pipelines ETL, que serão orquestrados pelo apache airflow, sendo todo o poder de processamento para suportar o ETL de batch de dados, diariamente, fornecido por máquinas virtuais do tipo G1X,G2X,G4X,G8X que vão de 4CPU'S e 16Gb de RAM até 32CPU'S e 128Gb de RAM. sendo extremamente menos custosos se tivéssemos escolhido utilizados máquinas virtuais dentro do seviço de EC2(Elastic Cloud Computing) da AWS

# Configurando ambiente
Para que seja possível construir o datalake dentro da aws, você deverá instalar os seguintes pré-requisitos:
  - Python em uma versão igual ou superior ao 3.11: https://www.python.org/downloads/
  - AWS CLI, seguindo o passo a passo de acordo com o seu sistema operacional: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

    ATENÇÃO!
    
    1)Caso o seu ambiente possua validação de usuários federados via AD, você deverá fazer a configuração dos usuários seguindo as instruções neste link:https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html
    2) Após a instalação do AWS CLI, não esqueça de configurar os seus parâmetros de usuário através do comando: aws configure, passando as suas chaves de acesso.Esse procedimento evita que seja necessário passar suas chaves de acesso como constantes dentro dos códigos python de implementação do ambiente. Instruções neste link:https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html
     
Após a instalação do python, você deverá instalar as seguintes bibliotecas Python: 
  - boto3: pip install boto3 ou python -m pip install boto3
    explicação: biblioteca python para integração com a AWS.
    
  - loggin: pip install logging ou python -m pip install logging
    explicação: biblioteca python utilizada para alertar falhs de login com o ambiente.
    
  - json: pip install json
    explicação: biblioteca python utilizada para passar os parâmetros de acesso dos usuários e definção dos grupos dentro da aws utilizando json.

  - apache-airflow-providers-amazon==8.16.0: pip install apache-airflow-providers-amazon==8.16.0 ou python -m pip install apache-airflow-providers-amazon==8.16.0
    explicação: biblioteca python que permitirá que o airflow faça o gerenciamento dos jobs que estarão sendo executados da AWS Glue, como jobs de ETL e Crawlers

    
