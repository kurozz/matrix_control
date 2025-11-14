#!/usr/bin/env python3
"""
config_loader.py - Carregamento e validação do arquivo config.yaml
"""

import sys
import os
import yaml


def load_config(config_path='config.yaml'):
    """
    Carrega e valida o arquivo de configuração YAML.

    Args:
        config_path (str): Caminho para o arquivo config.yaml

    Returns:
        dict: Dicionário com configurações validadas

    Exit codes:
        -6: Arquivo de configuração não encontrado ou inválido
    """
    # Verificar se arquivo existe
    if not os.path.exists(config_path):
        print(f"ERRO: Arquivo de configuração não encontrado: {config_path}")
        sys.exit(-6)

    # Carregar YAML
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERRO: Arquivo de configuração inválido: {e}")
        sys.exit(-6)
    except Exception as e:
        print(f"ERRO: Não foi possível ler arquivo de configuração: {e}")
        sys.exit(-6)

    # Validar estrutura básica
    if not isinstance(config, dict):
        print("ERRO: Configuração deve ser um dicionário")
        sys.exit(-6)

    return config


def validate_output_config(config):
    """
    Valida seção 'output' da configuração.

    Args:
        config (dict): Configuração completa

    Returns:
        dict: Configuração de saída validada

    Exit codes:
        -6: Configuração de saída inválida
    """
    if 'output' not in config:
        print("ERRO: Seção 'output' não encontrada no config.yaml")
        sys.exit(-6)

    output = config['output']

    # Validar pinout
    if 'pinout' not in output:
        print("ERRO: 'output.pinout' não encontrado no config.yaml")
        sys.exit(-6)

    pinout = output['pinout']

    # Validar rows e cols
    if 'rows' not in pinout or 'cols' not in pinout:
        print("ERRO: 'output.pinout.rows' e 'output.pinout.cols' são obrigatórios")
        sys.exit(-6)

    if not isinstance(pinout['rows'], list) or not isinstance(pinout['cols'], list):
        print("ERRO: 'rows' e 'cols' devem ser listas de GPIOs")
        sys.exit(-6)

    if len(pinout['rows']) == 0 or len(pinout['cols']) == 0:
        print("ERRO: 'rows' e 'cols' não podem estar vazios")
        sys.exit(-6)

    # Validar active_level
    if 'active_level' not in pinout:
        print("ERRO: 'output.pinout.active_level' é obrigatório")
        sys.exit(-6)

    if pinout['active_level'] not in ['HIGH', 'LOW']:
        print("ERRO: 'active_level' deve ser 'HIGH' ou 'LOW'")
        sys.exit(-6)

    return output


def validate_input_config(config):
    """
    Valida seção 'input' da configuração.

    Args:
        config (dict): Configuração completa

    Returns:
        dict: Configuração de entrada validada

    Exit codes:
        -6: Configuração de entrada inválida
    """
    if 'input' not in config:
        print("ERRO: Seção 'input' não encontrada no config.yaml")
        sys.exit(-6)

    input_cfg = config['input']

    # Validar input_matrix
    if 'input_matrix' not in input_cfg:
        print("ERRO: 'input.input_matrix' não encontrado no config.yaml")
        sys.exit(-6)

    matrix = input_cfg['input_matrix']

    # Validar rows e cols
    if 'rows' not in matrix or 'cols' not in matrix:
        print("ERRO: 'input.input_matrix.rows' e 'input.input_matrix.cols' são obrigatórios")
        sys.exit(-6)

    if not isinstance(matrix['rows'], list) or not isinstance(matrix['cols'], list):
        print("ERRO: 'rows' e 'cols' devem ser listas de GPIOs")
        sys.exit(-6)

    if len(matrix['rows']) == 0 or len(matrix['cols']) == 0:
        print("ERRO: 'rows' e 'cols' não podem estar vazios")
        sys.exit(-6)

    # Validar pull_mode
    if 'pull_mode' not in matrix:
        print("ERRO: 'input.input_matrix.pull_mode' é obrigatório")
        sys.exit(-6)

    if matrix['pull_mode'] not in ['UP', 'DOWN']:
        print("ERRO: 'pull_mode' deve ser 'UP' ou 'DOWN'")
        sys.exit(-6)

    # Validar closed_state
    if 'closed_state' not in matrix:
        print("ERRO: 'input.input_matrix.closed_state' é obrigatório")
        sys.exit(-6)

    if matrix['closed_state'] not in ['HIGH', 'LOW']:
        print("ERRO: 'closed_state' deve ser 'HIGH' ou 'LOW'")
        sys.exit(-6)

    # Validar monitor_interval (opcional, default=0.5)
    if 'monitor_interval' not in input_cfg:
        input_cfg['monitor_interval'] = 0.5

    return input_cfg


def get_matrix_dimensions(config, matrix_type='output'):
    """
    Retorna dimensões da matriz (num_rows, num_cols).

    Args:
        config (dict): Configuração completa
        matrix_type (str): 'output' ou 'input'

    Returns:
        tuple: (num_rows, num_cols)
    """
    if matrix_type == 'output':
        validated = validate_output_config(config)
        pinout = validated['pinout']
        return (len(pinout['rows']), len(pinout['cols']))
    elif matrix_type == 'input':
        validated = validate_input_config(config)
        matrix = validated['input_matrix']
        return (len(matrix['rows']), len(matrix['cols']))
    else:
        print(f"ERRO: matrix_type inválido: {matrix_type}")
        sys.exit(-1)
