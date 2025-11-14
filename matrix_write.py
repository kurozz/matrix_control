#!/usr/bin/env python3
"""
matrix_write.py - Script para controle de matriz de saída (LEDs, relés, etc)

Uso:
    python matrix_write.py <posição> <duração>
    python matrix_write.py reset

Exit codes:
    0: Sucesso
    -1: Erro genérico
    -2: Posição inválida
    -4: Duração inválida
    -5: Erro de hardware (GPIO)
    -6: Arquivo de configuração não encontrado
"""

import sys
import argparse
import time
import threading

# Importar módulos locais
import config_loader
import matrix_utils
import gpio_manager


def parse_arguments():
    """
    Faz parsing dos argumentos da linha de comando.

    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Controla ativação da matriz de saída',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python matrix_write.py A2 2.0     # Ativa A2 por 2 segundos
  python matrix_write.py 4 5.0      # Ativa posição 4 por 5 segundos
  python matrix_write.py reset      # Desativa todas as posições
        """
    )

    parser.add_argument('position', type=str, help='Posição (A1 ou 4) ou "reset"')
    parser.add_argument('duration', type=float, nargs='?', default=None,
                       help='Duração em segundos (obrigatório, exceto para reset)')

    args = parser.parse_args()

    # Comando especial: reset
    if args.position.lower() == 'reset':
        args.is_reset = True
        return args

    args.is_reset = False

    # Validar que duração é obrigatória quando não é reset
    if args.duration is None:
        print("ERRO: Duração em segundos é obrigatória")
        print("Uso: python matrix_write.py <posição> <duração>")
        print("Exemplo: python matrix_write.py A1 2.0")
        sys.exit(-1)

    return args


def activate_position(config, position_str, duration=None):
    """
    Ativa uma posição na matriz de saída.

    Args:
        config (dict): Configuração completa
        position_str (str): Posição a ativar (A1 ou 4)
        duration (float): Duração em segundos

    Exit codes:
        -2: Posição inválida
        -4: Duração inválida
        -5: Erro de GPIO
    """
    # Validar e obter configuração de saída
    output_cfg = config_loader.validate_output_config(config)
    pinout = output_cfg['pinout']
    rows = pinout['rows']
    cols = pinout['cols']
    active_level = pinout['active_level']
    safety_timeout = output_cfg.get('safety_timeout', None)

    num_rows = len(rows)
    num_cols = len(cols)

    # Converter posição para coordenadas
    row, col = matrix_utils.position_to_coords(position_str, num_rows, num_cols)
    position_alpha = matrix_utils.coords_to_position_alpha(row, col)

    # Validar duração se fornecida
    if duration is not None:
        if duration < 0.5 or duration > 600.0:
            print(f"ERRO: Duração inválida: {duration}s - deve estar entre 0.5s e 600s")
            sys.exit(-4)

    # Configurar GPIO
    gpio_manager.setup_output_matrix(rows, cols, active_level)

    # Ativar posição
    row_pin = rows[row]
    col_pin = cols[col]
    gpio_manager.activate_position(row_pin, col_pin, active_level)

    # Determinar duração efetiva (considerar safety_timeout)
    effective_duration = duration
    if safety_timeout is not None:
        if effective_duration is None:
            effective_duration = safety_timeout
        else:
            effective_duration = min(effective_duration, safety_timeout)

    # Mostrar mensagem
    print(f"Posição {position_alpha}: ATIVADA por {duration}s")

    # Criar thread para desativar automaticamente
    def auto_deactivate():
        time.sleep(effective_duration)
        # Desativar a posição
        gpio_manager.deactivate_position(row_pin, col_pin, active_level)

    timer_thread = threading.Thread(target=auto_deactivate, daemon=True)
    timer_thread.start()

    # Aguardar thread completar
    timer_thread.join()


def reset_all(config):
    """
    Desativa todas as posições da matriz.
    Útil quando a configuração foi alterada.

    Args:
        config (dict): Configuração completa
    """
    # Validar e obter configuração de saída
    output_cfg = config_loader.validate_output_config(config)
    pinout = output_cfg['pinout']
    rows = pinout['rows']
    cols = pinout['cols']
    active_level = pinout['active_level']

    # Configurar GPIO
    gpio_manager.setup_output_matrix(rows, cols, active_level)

    # Desativar todos os pinos
    gpio_manager.deactivate_all(rows, cols, active_level)

    print("Sistema resetado: todas as posições desativadas")


def main():
    """
    Função principal do script.
    """
    # Parse argumentos
    args = parse_arguments()

    # Carregar configuração
    config = config_loader.load_config('config.yaml')

    # Executar ação
    if args.is_reset:
        # Comando especial: reset
        reset_all(config)
    else:
        # Ativar posição com duração especificada
        activate_position(config, args.position, args.duration)

    # Cleanup
    gpio_manager.cleanup_gpio()
    sys.exit(0)


if __name__ == '__main__':
    main()
