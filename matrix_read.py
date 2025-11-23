#!/usr/bin/env python3
"""
matrix_read.py - Script para leitura de matriz de entrada (keypad, etc)

Uso:
    python matrix_read.py                    # Leitura única (JSON)
    python matrix_read.py --interval 1.0     # Modo contínuo (monitor visual)

Exit codes:
    0: Saída normal (Ctrl+C)
    -5: Erro crítico ao ler sensores
    -6: Arquivo de configuração não encontrado
"""

import sys
import argparse
import json
import time
import os
from signal import signal, SIGINT

# Importar módulos locais
import config_loader
import gpio_manager


def parse_arguments():
    """
    Faz parsing dos argumentos da linha de comando.

    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Lê matriz de entrada e retorna o estado atual',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python matrix_read.py                    # Leitura única (JSON)
  python matrix_read.py --interval 1.0     # Monitor com intervalo de 1s
  python matrix_read.py --interval 0.2     # Monitor rápido (0.2s)
        """
    )

    parser.add_argument(
        '--interval',
        type=float,
        default=None,
        metavar='SECONDS',
        help='Habilita modo contínuo com intervalo especificado (ex: 0.5)'
    )

    return parser.parse_args()


def read_single(config):
    """
    Faz leitura única da matriz e retorna JSON.

    Args:
        config (dict): Configuração completa

    Returns:
        dict: Estado da matriz em formato JSON
    """
    # Validar configuração de entrada
    input_cfg = config_loader.validate_input_config(config)
    matrix_cfg = input_cfg['input_matrix']

    rows = matrix_cfg['rows']
    cols = matrix_cfg['cols']
    pull_mode = matrix_cfg['pull_mode']
    closed_state = matrix_cfg['closed_state']

    # Configurar GPIO
    gpio_manager.setup_input_matrix(rows, cols, pull_mode)

    # Ler matriz
    matrix_state = gpio_manager.read_matrix(rows, cols, closed_state)

    return {'matrix': matrix_state}


def clear_screen():
    """
    Limpa a tela do terminal.
    """
    os.system('clear' if os.name != 'nt' else 'cls')


def print_monitor_header(interval, num_cols):
    """
    Imprime cabeçalho do monitor.

    Args:
        interval (float): Intervalo de atualização
        num_cols (int): Número de colunas da matriz
    """
    # Calcular largura baseada no número de colunas
    # Cada coluna: letra (1) + espaço (6) = 7 chars
    # Prefixo da linha: "│     " = 6 chars
    # Sufixo: " │" = 2 chars
    content_width = 6 + (num_cols * 7) + 2
    box_width = max(46, content_width)

    # Linha superior
    print("┌" + "─" * (box_width - 2) + "┐")

    # Título
    title = "   Matrix Monitor"
    padding = box_width - len(title) - 2
    print(f"│{title}{' ' * padding}│")

    # Info
    info = f"   Update interval: {interval}s | Ctrl+C to exit"
    padding = box_width - len(info) - 2
    print(f"│{info}{' ' * padding}│")

    # Divisor
    print("├" + "─" * (box_width - 2) + "┤")

    return box_width


def print_matrix_visual(matrix_state, num_rows, num_cols, box_width):
    """
    Imprime representação visual da matriz com emojis.

    Args:
        matrix_state (list): Estado da matriz 2D
        num_rows (int): Número de linhas
        num_cols (int): Número de colunas
        box_width (int): Largura da caixa
    """
    # Cabeçalho de colunas (A, B, C, ...)
    col_headers = "     "
    for col in range(num_cols):
        col_letter = chr(ord('A') + col)
        col_headers += f"{col_letter}      "

    padding = box_width - len(col_headers) - 2
    print(f"│{col_headers}{' ' * padding}│")

    # Linhas da matriz
    for row in range(num_rows):
        row_str = f" {row + 1}  "
        for col in range(num_cols):
            if matrix_state[row][col] == 'on':
                row_str += "[X]    "
            else:
                row_str += "[ ]    "

        # Preencher espaço restante
        padding = box_width - len(row_str) - 2
        print(f"│{row_str}{' ' * padding}│")

    # Rodapé
    print("└" + "─" * (box_width - 2) + "┘")


def monitor_continuous(config, interval):
    """
    Monitora matriz continuamente com display visual.

    Args:
        config (dict): Configuração completa
        interval (float): Intervalo entre leituras em segundos
    """
    # Validar configuração de entrada
    input_cfg = config_loader.validate_input_config(config)
    matrix_cfg = input_cfg['input_matrix']

    rows = matrix_cfg['rows']
    cols = matrix_cfg['cols']
    pull_mode = matrix_cfg['pull_mode']
    closed_state = matrix_cfg['closed_state']

    num_rows = len(rows)
    num_cols = len(cols)

    # Configurar GPIO
    gpio_manager.setup_input_matrix(rows, cols, pull_mode)

    # Handler para Ctrl+C
    def signal_handler(sig, frame):
        print("\n\nSaindo...")
        gpio_manager.cleanup_gpio()
        sys.exit(0)

    signal(SIGINT, signal_handler)

    # Loop de monitoramento
    try:
        while True:
            clear_screen()
            box_width = print_monitor_header(interval, num_cols)

            # Ler matriz
            matrix_state = gpio_manager.read_matrix(rows, cols, closed_state)

            # Mostrar estado visual
            print_matrix_visual(matrix_state, num_rows, num_cols, box_width)

            # Aguardar próximo ciclo
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nSaindo...")
        gpio_manager.cleanup_gpio()
        sys.exit(0)


def main():
    """
    Função principal do script.
    """
    # Parse argumentos
    args = parse_arguments()

    # Carregar configuração
    config = config_loader.load_config('config.yaml')

    # Decidir modo de operação
    if args.interval is not None:
        # Modo contínuo (monitor)
        if args.interval < 0.1 or args.interval > 60.0:
            print("ERRO: Intervalo inválido - deve estar entre 0.1s e 60s")
            sys.exit(-1)

        monitor_continuous(config, args.interval)
    else:
        # Modo leitura única (usar intervalo padrão do config se não especificado)
        input_cfg = config_loader.validate_input_config(config)
        default_interval = input_cfg.get('monitor_interval', 0.5)

        # Verificar se usuário quer modo monitor com intervalo padrão
        # Neste caso, como não há --interval, fazemos leitura única
        result = read_single(config)
        print(json.dumps(result, indent=3))

        # Cleanup
        gpio_manager.cleanup_gpio()
        sys.exit(0)


if __name__ == '__main__':
    main()
