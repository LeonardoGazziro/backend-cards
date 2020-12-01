def valid_new_card_request(json):
    """
    Valida se todos os parametros foram passados no JSON de solicitação de novo cartão

    *** Essa etapa de validação por código poderia ser retirada e feita no API Gateway da AWS utilizando um JSON de validação.
    O exemplo desse arquivo é o schemaNewCard.json
    Validar através do arquivo Schema impede a execução da lambda, diminuindo custos.

    :param json: JSON com as informações que serão validadas
    :return: True ou false e a mensagem contendo o parametro que não foi informado em caso de JSON invalido
    """
    required_params = ['name', 'phone', 'age', 'cpf', 'income']
    valid, msg = True, ''

    for param in required_params:
        if param not in json.keys():
            valid = False
            msg = f'Parametro {param} é obrigatório, favor informa-lo!'

    return valid, msg


def numeric_to_currency(val):
    """
    Converte um valor numerico para valor monetário
    :param val:
    :return:
    """
    if isinstance(val, str):
        return val

    return f'R$ {val:.2f}'.replace('.', ',')


def score_to_text(score, income):
    """
    1 a 299 	Reprovado
    300 a 599 	R$1000,00
    600 a 799 	50% da renda informada, valor mínimo R$1000,00
    800 a 950 	200% da renda informada
    951 a 999 	Sem limites, considerar R$ 1.000.000
    :param score: valor do score
    :param score: valor da renda
    :return: O texto referente ao Score
    """
    credito = 'Reprovado'
    if 300 <= score <= 599:
        credito = 1000
    elif 600 <= score <= 799:
        val = income * 0.5
        credito = val if val > 1000 else 1000
    elif 800 <= score <= 950:
        credito = income * 2.0
    elif 951 <= score <= 999:
        credito = 1000000

    return numeric_to_currency(credito)
