import json
import os

CAMPOS_OBRIGATORIOS = [
    'loja',
    'ip',
    'usuario',
    'senha',
    'caminho_bin'
]

def carregar_lojas(caminho_arquivo='config/lojas.json'):
    """
    Carrega e valida o arquivo de configuração das lojas.
    Retorna uma lista de dicionários com dados das lojas.
    """

    # Verificar se o arquivo existe
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(
            f'Arquivo de configuração não encontrado: {caminho_arquivo}'
        )
    
    # Abre e carrega o json
    try:
        with open(caminho_arquivo, encoding='utf-8') as arquivo:
            lojas = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(f'JSON inválido: {erro}')
    
    # Valida se e uma lista
    if not isinstance(lojas, list):
        raise ValueError('O arquivo de lojas deve conter uma LISTA')
    
    # Valida cada loja
    for indice, loja in enumerate(lojas):
        if not isinstance(loja, dict):
            raise ValueError(f'Loja na posição {indice} não é um objeto válido')
        
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in loja:
                raise ValueError(
                    f'Campo "{campo}" ausente na loja {loja.get("loja", indice)}'
                )
        
        if not str(loja[campo]).strip():
            raise ValueError(
                f'Campo "{campo}" vazio na loja {loja.get("loja", indice)}'
            )
    
    return lojas