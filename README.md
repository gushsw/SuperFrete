# DataLake SuperFrete
Os arquivos que estão neste repositório tem como objetivo implementar uma arquitetura de dados de datalake AWS, projetada para suportar um ambiente de big data, incluindo:
  1) processamento em larga escala, 
  2) atualização em batch's diários, 
  3) análise de dados
sendo este pontos possíveis através de um pipeline orquestrado com Apache Airflow.

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

    
