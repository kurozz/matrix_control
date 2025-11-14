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
    -3: Posição já ativada
    -4: Duração inválida
    -5: Erro de hardware (GPIO)
    -6: Arquivo de configuração não encontrado
"""

import sys
import argparse
import time
import threading
import os
import json
from pathlib import Path

# Importar módulos locais
import config_loader
import matrix_utils
import gpio_manager


# Arquivo para rastrear estado da matriz
STATE_FILE = '/tmp/matrix_write_state.json'


def load_state():
    """
    Carrega o estado atual da matriz do arquivo.

    Returns:
        dict: Estado com 'active_position', 'row', 'col', 'timer_thread'
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass

    return {
        'active_position': None,
        'row': None,
        'col': None,
        'timestamp': None
    }


def save_state(state):
    """
    Salva o estado atual da matriz no arquivo.

    Args:
        state (dict): Estado a ser salvo
    """
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"AVISO: Não foi possível salvar estado: {e}")


def clear_state():
    """
    Limpa o arquivo de estado.
    """
    try:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    except:
        pass


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
  python matrix_write.py reset      # Desativa tudo e limpa estado
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


def deactivate_position_internal(config, state, show_message=True):
    """
    Desativa a posição atualmente ativa (função interna).

    Args:
        config (dict): Configuração completa
        state (dict): Estado atual
        show_message (bool): Se deve mostrar mensagem de desativação
    """
    if state['active_position'] is None:
        return

    # Obter configuração de saída
    output_cfg = config_loader.validate_output_config(config)
    pinout = output_cfg['pinout']
    rows = pinout['rows']
    cols = pinout['cols']
    active_level = pinout['active_level']

    # Desativar GPIO
    row_pin = rows[state['row']]
    col_pin = cols[state['col']]
    gpio_manager.deactivate_position(row_pin, col_pin, active_level)

    if show_message:
        print(f"Posição {state['active_position']}: DESATIVADA")

    # Limpar estado
    clear_state()


def activate_position(config, position_str, duration=None):
    """
    Ativa uma posição na matriz de saída.

    Args:
        config (dict): Configuração completa
        position_str (str): Posição a ativar (A1 ou 4)
        duration (float): Duração em segundos (None = indefinido)

    Exit codes:
        -2: Posição inválida
        -3: Posição já ativada
        -4: Duração inválida
        -5: Erro de GPIO
    """
    # Validar e obter configuração de saída
    output_cfg = config_loader.validate_output_config(config)
    pinout = output_cfg['pinout']
    rows = pinout['rows']
    cols = pinout['cols']
    active_level = pinout['active_level']
    force_off_on_conflict = output_cfg.get('force_off_on_conflict', True)
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

    # Carregar estado atual
    state = load_state()

    # Verificar se esta posição já está ativa
    if state['active_position'] == position_alpha:
        print(f"ERRO: Posição {position_alpha} já está ativada")
        sys.exit(-3)

    # Verificar se outra posição está ativa
    if state['active_position'] is not None:
        if force_off_on_conflict:
            # Desativar a posição anterior
            deactivate_position_internal(config, state, show_message=False)
        else:
            print(f"ERRO: Posição {state['active_position']} já está ativada")
            print(f"Desative-a antes de ativar outra posição")
            sys.exit(-3)

    # Configurar GPIO
    gpio_manager.setup_output_matrix(rows, cols, active_level)

    # Ativar posição
    row_pin = rows[row]
    col_pin = cols[col]
    gpio_manager.activate_position(row_pin, col_pin, active_level)

    # Salvar novo estado
    new_state = {
        'active_position': position_alpha,
        'row': row,
        'col': col,
        'timestamp': time.time()
    }
    save_state(new_state)

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
        # Recarregar estado para verificar se ainda é a mesma posição
        current_state = load_state()
        if current_state['active_position'] == position_alpha:
            deactivate_position_internal(config, current_state, show_message=False)

    timer_thread = threading.Thread(target=auto_deactivate, daemon=True)
    timer_thread.start()

    # Aguardar thread completar
    timer_thread.join()


def reset_all(config):
    """
    Desativa todas as posições e limpa o estado.
    Útil quando a configuração foi alterada e o estado está inconsistente.

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

    # Limpar estado
    clear_state()

    print("Sistema resetado: todas as posições desativadas e estado limpo")


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
