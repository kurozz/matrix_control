#!/usr/bin/env python3
"""
matrix_utils.py - Funções auxiliares para manipulação de posições em matrizes
"""

import sys
import string


def position_to_coords(position, num_rows, num_cols):
    """
    Converte posição (A1 ou 4) para coordenadas (row, col).

    Formato alfanumérico: A1, B2, C3 (Coluna + Linha)
    Formato numérico: 1-9 para 3x3 (ordem por linhas)

    Exemplo para matriz 3x3:
        A   B   C
    1  [1] [2] [3]
    2  [4] [5] [6]
    3  [7] [8] [9]

    Args:
        position (str): Posição no formato A1 ou 4
        num_rows (int): Número de linhas da matriz
        num_cols (int): Número de colunas da matriz

    Returns:
        tuple: (row, col) - índices começam em 0

    Exit codes:
        -2: Posição inválida
    """
    position = str(position).strip().upper()

    # Tentar formato alfanumérico (A1, B2, etc)
    if len(position) >= 2 and position[0].isalpha() and position[1:].isdigit():
        col_letter = position[0]
        row_num = int(position[1:])

        # Converter letra para índice de coluna (A=0, B=1, C=2, ...)
        col = ord(col_letter) - ord('A')
        row = row_num - 1  # Linhas começam em 1

        # Validar limites
        if row < 0 or row >= num_rows:
            print(f"ERRO: Posição {position} inválida - linha fora dos limites (1-{num_rows})")
            sys.exit(-2)

        if col < 0 or col >= num_cols:
            max_col = chr(ord('A') + num_cols - 1)
            print(f"ERRO: Posição {position} inválida - coluna fora dos limites (A-{max_col})")
            sys.exit(-2)

        return (row, col)

    # Tentar formato numérico (1, 2, 3, ...)
    elif position.isdigit():
        pos_num = int(position)

        # Validar limite
        max_pos = num_rows * num_cols
        if pos_num < 1 or pos_num > max_pos:
            print(f"ERRO: Posição {position} inválida - deve estar entre 1 e {max_pos}")
            sys.exit(-2)

        # Converter para coordenadas (ordem por linhas)
        # Posição 1 = (0,0), 2 = (0,1), 3 = (0,2), 4 = (1,0), etc
        pos_index = pos_num - 1  # Converter para base 0
        row = pos_index // num_cols
        col = pos_index % num_cols

        return (row, col)

    else:
        print(f"ERRO: Posição {position} inválida - formato deve ser A1 ou 4")
        sys.exit(-2)


def coords_to_position_alpha(row, col):
    """
    Converte coordenadas (row, col) para formato alfanumérico (A1).

    Args:
        row (int): Índice da linha (base 0)
        col (int): Índice da coluna (base 0)

    Returns:
        str: Posição no formato A1
    """
    col_letter = chr(ord('A') + col)
    row_num = row + 1
    return f"{col_letter}{row_num}"


def coords_to_position_numeric(row, col, num_cols):
    """
    Converte coordenadas (row, col) para formato numérico (4).

    Args:
        row (int): Índice da linha (base 0)
        col (int): Índice da coluna (base 0)
        num_cols (int): Número de colunas da matriz

    Returns:
        int: Posição numérica
    """
    return (row * num_cols) + col + 1


def validate_duration(duration_str):
    """
    Valida duração em segundos.

    Args:
        duration_str (str): Duração como string

    Returns:
        float: Duração validada em segundos

    Exit codes:
        -4: Duração inválida
    """
    try:
        duration = float(duration_str)
    except ValueError:
        print(f"ERRO: Duração inválida: {duration_str}")
        sys.exit(-4)

    # Validar range: 0.5s a 600s (10 minutos)
    if duration < 0.5 or duration > 600.0:
        print(f"ERRO: Duração inválida: {duration}s - deve estar entre 0.5s e 600s")
        sys.exit(-4)

    return duration


def validate_interval(interval_str):
    """
    Valida intervalo de monitoramento em segundos.

    Args:
        interval_str (str): Intervalo como string

    Returns:
        float: Intervalo validado em segundos

    Exit codes:
        -1: Intervalo inválido
    """
    try:
        interval = float(interval_str)
    except ValueError:
        print(f"ERRO: Intervalo inválido: {interval_str}")
        sys.exit(-1)

    # Validar range razoável: 0.1s a 60s
    if interval < 0.1 or interval > 60.0:
        print(f"ERRO: Intervalo inválido: {interval}s - deve estar entre 0.1s e 60s")
        sys.exit(-1)

    return interval


def get_matrix_size_str(num_rows, num_cols):
    """
    Retorna string descritiva do tamanho da matriz.

    Args:
        num_rows (int): Número de linhas
        num_cols (int): Número de colunas

    Returns:
        str: String no formato "3x3" ou "4x5"
    """
    return f"{num_rows}x{num_cols}"


def get_all_positions_alpha(num_rows, num_cols):
    """
    Retorna lista de todas as posições em formato alfanumérico.

    Args:
        num_rows (int): Número de linhas
        num_cols (int): Número de colunas

    Returns:
        list: Lista de posições ['A1', 'A2', 'A3', 'B1', ...]
    """
    positions = []
    for row in range(num_rows):
        for col in range(num_cols):
            positions.append(coords_to_position_alpha(row, col))
    return positions
