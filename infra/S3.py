import boto3
import json
from os import getenv


class AWSConnection:
    """
    Classe para criar um cliente AWS
    """
    def __init__(self, resource):
        self.access_key = getenv('S3_AWS_ACCESS_KEY', '')
        self.secret_key = getenv('S3_AWS_SECRET_KEY', '')
        self.resource = resource
        self.aws_session = boto3.session.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1'
        )

    def get_client(self):
        """
        Retorna o cliente da AWS
        :return: Cliente da AWS
        """
        return self.aws_session.client(self.resource)


class S3:
    """
    Classe para criar uma conexão com o S3
    """
    def __init__(self, bucket):
        self.AWS_session = AWSConnection('s3')
        self.s3_client = None
        self.s3_bucket = bucket

    def create_s3_instance(self):
        """
        Cria a instancia de client S3
        :return:
        """
        self.s3_client = self.AWS_session.get_client()

    def get_s3_obj(self, s3_path, file_name):
        """
        Pega um objeto do S3
        :param s3_path: caminho do arquivo s3
        :param file_name: nome do arquivo
        :return: retornar o arquivo do S3
        """
        result = False
        msg = None
        # Formata o nome do arquivo
        file_path = s3_path + file_name if s3_path != '' else file_name
        if '.json' not in file_path:
            file_path += '.json'
        try:
            # Busca o arquivo do S3
            response = self.s3_client.get_object(Key=file_path, Bucket=self.s3_bucket)
            if response:
                obj = json.loads(response['Body'].read().decode('utf-8'))
                result = obj
        except Exception as err:
            msg = str(err)

        return result, msg

    def put_s3_obj(self, s3_path, obj, file_name):
        """
        Insere o Objeto no s3
        :param s3_path: caminho do s3
        :param obj: Objeto a ser inserido.
        :param file_name: nome do arquivo no s3
        :return: Retorna True ou False informando se foi inserido ou não
        """
        result = False
        msg = None
        # Formata o nome do arquivo
        file_path = s3_path + file_name if s3_path != '' else file_name
        if '.json' not in file_path:
            file_path += '.json'
        try:
            # Insere o arquivo no S3
            response = self.s3_client.put_object(Key=file_path, Bucket=self.s3_bucket, Body=json.dumps(obj))
            result = response
            msg = 'Inserido com sucesso!'
        except Exception as err:
            msg = str(err)

        return result, msg

    def get_bucket_files(self, bucket):
        """
        Retorna o nome de todos os arquivos de um bucket
        :param bucket: Nome do bucket
        :return: Tupla com o resultado e a mensagem.
        """
        result = False
        msg = None
        try:
            # lista todos os objetos do bucket passado
            response = self.s3_client.list_objects(Bucket=bucket)
            if 'Contents' in response.keys():
                result = response['Contents']
                msg = 'OK!'
        except Exception as err:
            msg = str(err)

        return result, msg

    def delete_s3_obj(self, s3_path, file_name):
        """
        Deleta um objeto do S3
        :param s3_path: Caminho do Arquivo no s3
        :param file_name: nome do arquivo no s3
        :return: Tupla com o resultado e a mensagem.
        """
        result = False
        msg = None
        # Formata o nome do arquivo
        file_path = s3_path + file_name if s3_path != '' else file_name
        if '.json' not in file_path:
            file_path += '.json'
        try:
            # Insere o arquivo no S3
            response = self.s3_client.delete_object(Key=file_path, Bucket=self.s3_bucket)
            result = response
            msg = 'Objeto deletado com sucesso!'
        except Exception as err:
            msg = str(err)

        return result, msg
