"""
Pensando no uso de micro serviços, esse arquivo contem o conteudo (python) das funções que serão colocadas na AWS
utilizando o framework Serverless.
O frameWork Serverless é utilizado para fazer o deploy do código na AWS, sua utilização é interessante, pois o framework
pode ser utilizado para outros serviços como Google Cloud e Azure, sem grandes alterações no arquivo YML
"""

import uuid
from os import getenv
from infra.S3 import S3
from utils import valid_new_card_request, score_to_text
from random import randint


def get_requests_card_list_handler(event, context):
    """
    GET - Esse código será chamado através de um GET para a API que sera criada no arquivo serverless
    Retorna a lista das solicitações de cartão realizadas
    :param event: Event recebido pela nuvem
    :param context: Contexto com informações da função
    :return: JSON contendo a lista das das solicitações.
    """
    try:
        s3_bucket = getenv('S3_BUCKET', '')

        s3 = S3(s3_bucket)
        s3.create_s3_instance()
        request_list, msg = s3.get_bucket_files(s3_bucket)
        _requests = list()
        for request in request_list:
            obj, msg = s3.get_s3_obj('', request['Key'])
            _requests.append(obj)

        if _requests:
            return {'status': 200, 'requests_list': _requests}
        else:
            return {'status': 404, 'msg': 'Lista de  requisições não encontrada'}
    except Exception as err:
        return {'status': 500, 'msg': 'Erro interno ao processar a requisição'}


def request_new_card_handler(event, context):
    """
    POST - Esse código será chamado através de um POST para a API que será criada no arquivo serverless.
    Faz a requisição de um novo cartão, o Score do candidato será avaliado.
    :param event: Event recebido pela nuvem
    :param context: Contexto com informações da função
    :return: JSON contendo informações sobre a solicitação realizada, se o pedido de cartão foi aprovado ou não.
    """
    try:
        body = event.get('body', {})
        s3_bucket = getenv('S3_BUCKET', '')
        if body:
            # Verifica se o JSON é valido
            json_valido, msg = valid_new_card_request(body)
            if json_valido:
                body['id'] = str(uuid.uuid4())

                s3 = S3(s3_bucket)
                s3.create_s3_instance()
                # insere o JSON no S3
                resp, msg = s3.put_s3_obj('', body, body['cpf'])
                print(resp)
                print(msg)
                json_ret = {'status': 200, 'msg': 'Requisição enviada para aprovação!'}
            else:
                json_ret = {'status': 500, 'msg': msg}
        else:
            json_ret = {'status': 500, 'msg': 'Json inválido!'}

        return json_ret
    except Exception as err:
        return {'status': 500, 'msg': 'Erro interno ao processar a requisição'}


def delete_card_request_handler(event, context):
    """
    DELETE - Esse código será chamado através de um DELETE para a API que será criada no arquivo serverless.
    Faz a requisição para apagar uma solicitação de cartão.
    :param event: Event recebido pela nuvem
    :param context: Contexto com informações da função
    :return: JSON contendo informações sobre a solicitação realizada, se o pedido de cartão foi excluído ou não.
    """
    try:
        s3_bucket_crawler = getenv('S3_BUCKET', '')

        request_json, msg = None, None
        path = event.get('path', {})
        if 'id' in path.keys():
            s3 = S3(s3_bucket_crawler)
            s3.create_s3_instance()
            del_response, msg = s3.delete_s3_obj('', path['id'])

        if del_response['ResponseMetadata']['HTTPStatusCode'] == 204:
            return {'status': 200, 'msg': 'Requisição deletada!'}
        else:
            return {'status': 404, 'msg': 'Requisição não encontrado'}
    except Exception as err:
        return {'status': 500, 'msg': 'Erro interno ao processar a requisição'}


def process_card_request_handler(event, context):
    """
    Realiza o processamento de um pedido de novo cartão.
    Esse código é ativado quando um novo arquivo de pedido é salvo no S3
    :param event: Event recebido pela nuvem
    :param context: Contexto com informações da função
    :return: None.
    """
    try:
        for obj in event['Records']:
            # Informações do arquivo que foi inserido no S3
            bucket_name = obj['s3']['bucket']['name']
            obj = obj['s3']['object']['key']

            s3 = S3(bucket_name)
            s3.create_s3_instance()
            obj_json, msg = s3.get_s3_obj('', obj)
            # faz os Score do cliente
            score = randint(1, 999)
            obj_json['credit'] = score_to_text(score, obj_json['income'])
            resp, msg = s3.put_s3_obj('', obj_json, obj_json['cpf'])
    except Exception as err:
         print({'status': 500, 'msg': 'Erro interno ao processar a requisição', "error": f'{err}'})


def get_new_card_request_response_handler(event, context):
    """
    GET - Esse código será chamado através de um GET para a API que será criada no arquivo serverless.
    Recebe o id do solicitante via parametro de URL e retorna as informações referente ao solicitante e seu crédito
    :param event: Event recebido pela nuvem
    :param context: Contexto com informações da função
    :return: informações do solicitante
    """
    try:
        s3_bucket_crawler = getenv('S3_BUCKET', '')

        print(event)
        request_json, msg = None, None
        path = event.get('path', {})
        if 'id' in path.keys():
            s3 = S3(s3_bucket_crawler)
            s3.create_s3_instance()
            request_json, msg = s3.get_s3_obj('', path['id'])

        if request_json:
            request_json['status'] = 200
            return request_json
        else:
            return {'status': 404, 'msg': 'Requisição não encontrada'}
    except Exception as err:
        return {'status': 500, 'msg': 'Erro interno ao processar a requisição'}


if __name__ == '__main__':
    ex_event = {'body':
        {
            'name': 'Leonardo Roberto Gazziro',
            'phone': '99999999999',
            'age': 26,
            'cpf': '999.999.999-99',
            'income': 3000
        },
        'method': 'POST', 'principalId': '',
        'stage': 'dev',
        'cognitoPoolClaims': {'sub': ''},
        'enhancedAuthContext': {},
        'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache', 'CloudFront-Forwarded-Proto': 'https',
                    'CloudFront-Is-Desktop-Viewer': 'true',
                    'CloudFront-Is-Mobile-Viewer': 'false',
                    'CloudFront-Is-SmartTV-Viewer': 'false',
                    'CloudFront-Is-Tablet-Viewer': 'false',
                    'CloudFront-Viewer-Country': 'BR',
                    'Content-Type': 'application/json',
                    'Host': '1nhucniq8b.execute-api.us-east-1.amazonaws.com',
                    'Postman-Token': '0d40ddc9-494c-438c-9e34-30f9f44ea018',
                    'User-Agent': 'PostmanRuntime/7.26.3',
                    'Via': '1.1 3fff6e22f8d6795a61bfdca17d362ca5.cloudfront.net (CloudFront)',
                    'X-Amz-Cf-Id': 'OKNx6jkzKLQ3nbtD0t4JTNynGlc2TZDSemAepsPC-8Kv0ZV1f6Tz7w==',
                    'X-Amzn-Trace-Id': 'Root=1-5f4bf435-7d8aa2621cebaaabfa719a0c',
                    'X-Forwarded-For': '138.204.24.213, 64.252.179.69',
                    'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'},
        'query': {},
        'path': {},
        'identity': {'cognitoIdentityPoolId': '', 'accountId': '', 'cognitoIdentityId': '', 'caller': '',
                     'sourceIp': '138.204.24.213', 'principalOrgId': '', 'accessKey': '',
                     'cognitoAuthenticationType': '', 'cognitoAuthenticationProvider': '', 'userArn': '',
                     'userAgent': 'PostmanRuntime/7.26.3', 'user': ''},
        'stageVariables': {},
        'requestPath': ''}

    ex_event_s3 = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1',
                    'eventTime': '2020-09-06T18:11:57.722Z', 'eventName': 'ObjectCreated:Put',
                    'userIdentity': {'principalId': 'A1GN6EPM0JKA8K'},
                    'requestParameters': {'sourceIPAddress': '177.42.49.149'},
                    'responseElements': {'x-amz-request-id': '7857E87B7E4BA60D',
                                         'x-amz-id-2': 'lmNysI3mKLmMQoOzCtPnjT8usl2fMUYbIyipfE59v3oWuyu44XxI/L2tXxRPkqjC6uUNu3rGB/eekMpWqOj6RceGfrLLLTeg'},
                    's3': {'s3SchemaVersion': '1.0',
                           'configurationId': 'cc7a7b1c-d354-413c-94e0-c4c2e3cf153a',
                           'bucket': {'name': 'cards-requests-leogazziro',
                                      'ownerIdentity': {'principalId': 'A1GN6EPM0JKA8K'},
                                      'arn': 'arn:aws:s3:::novo-produto'},
                           'object': {'key': '999.999.999-99.json', 'size': 1172,
                                      'eTag': 'f64c165d9209eb645b660f04b27dc8d2',
                                      'sequencer': '005F552670F6AF15F4'}}}]}

    ex_event_att_price = {'body': {},
                          'method': 'GET',
                          'principalId': '',
                          'stage': 'dev',
                          'cognitoPoolClaims': {'sub': ''},
                          'enhancedAuthContext': {},
                          'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-Country': 'BR', 'Host': 'ug0whmmoab.execute-api.us-east-1.amazonaws.com', 'Postman-Token': 'b4156348-2b52-4528-9fe5-f990b6e0b002', 'User-Agent': 'PostmanRuntime/7.26.8', 'Via': '1.1 563ebd37505bdef43c0d2cf809086a89.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': '3GsBNWObU21N4Duq6GXK-NVydq7LdeTnEVsiU9o4i3WB4WZcY95iLQ==', 'X-Amzn-Trace-Id': 'Root=1-5fc44260-324117fb66e2aaa37e74b01d', 'X-Forwarded-For': '177.220.174.33, 64.252.179.71', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'},
                          'query': {},
                          'path': {'id': '999.999.999-99'},
                          'identity': {'cognitoIdentityPoolId': '', 'accountId': '', 'cognitoIdentityId': '', 'caller': '', 'sourceIp': '177.220.174.33', 'principalOrgId': '', 'accessKey': '', 'cognitoAuthenticationType': '', 'cognitoAuthenticationProvider': '', 'userArn': '', 'userAgent': 'PostmanRuntime/7.26.8', 'user': ''}, 'stageVariables': {}, 'requestPath': '/get_new_card_request_response/{id}'}

    # request_new_card_handler(ex_event, '')
    # get_requests_card_list_handler('', '')
    # process_card_request(ex_event_s3, '')
    # get_new_card_request_response_handler(ex_event_att_price, '')
    # delete_card_request_handler(ex_event_att_price, '')

