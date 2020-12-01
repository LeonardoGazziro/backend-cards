# Introdução
Essa API contempla as requisições basicas para registro de um cartão para novos clientes

# Overview
## request_new_card
Chamada: POST
Caminho: /dev/request_new_card
Objetivo: Cadastrar a requisição de um novo cartão
Deve ser enviado um JSON no seguinte formato:
```
{
    'name': 'Leonardo Roberto Gazziro',
    'phone': '99999999999',
    'age': 26,
    'cpf': '999.999.999-99',
    'income': 3000
}
```

## get_new_card_request_response
Chamada: GET
Caminho: /dev/get_new_card_request_response/{cpf}
Objetivo: Retorna o Status de uma requisição enviada
Obs: enviad o cpf com ponto e traço

## get_requests_card_list
Chamada: GET
Caminho: /dev/get_new_card_request_response
Objetivo: Retorna todas as requisições de cartão enviadas

## delete_card_request
Chamada: DELETE
Caminho: /dev/delete_card_request/{cpf}
Objetivo: Deleta uma requisição feita utilizando o parametro passado na URL
Obs: enviad o cpf com ponto e traço


# Autenticação
Não é necessaria

# Códigos de erro
A API possui o status de erro 500 - informando que houve um erro interno no processo.
