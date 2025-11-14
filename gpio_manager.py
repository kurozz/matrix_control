#!/usr/bin/env python3
"""
gpio_manager.py - Gerenciamento de GPIO para Raspberry Pi
"""

import sys
import atexit

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError) as e:
    print(f"ERRO: Não foi possível importar RPi.GPIO: {e}")
    print("Certifique-se de estar rodando em um Raspberry Pi com RPi.GPIO instalado")
    sys.exit(-5)


# Flag para rastrear se GPIO foi inicializado
_gpio_initialized = False


def setup_gpio():
    """
    Inicializa GPIO em modo BCM e registra cleanup automático.

    Exit codes:
        -5: Erro ao acessar GPIO
    """
    global _gpio_initialized

    if _gpio_initialized:
        return

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        _gpio_initialized = True

        # Registrar cleanup automático ao sair
        atexit.register(cleanup_gpio)

    except Exception as e:
        print(f"ERRO: Não foi possível inicializar GPIO: {e}")
        print("Verifique permissões (sudo usermod -a -G gpio $USER)")
        sys.exit(-5)


def cleanup_gpio():
    """
    Limpa configurações de GPIO.
    """
    global _gpio_initialized

    if _gpio_initialized:
        try:
            GPIO.cleanup()
            _gpio_initialized = False
        except:
            pass  # Ignorar erros no cleanup


def setup_output_matrix(rows, cols, active_level):
    """
    Configura matriz de saída (rows como OUTPUT, cols como OUTPUT).

    Para matriz de ânodo comum (cols=anodos, rows=catodos):
    - Colunas fornecem corrente (active_level aplica aqui)
    - Linhas drenam corrente (lógica invertida)

    Args:
        rows (list): Lista de GPIOs para linhas (catodos/dreno)
        cols (list): Lista de GPIOs para colunas (anodos/fonte)
        active_level (str): 'HIGH' ou 'LOW' (aplicado às colunas)

    Exit codes:
        -5: Erro ao configurar GPIO
    """
    setup_gpio()

    try:
        # Estado inativo para LINHAS (catodos): oposto do active_level
        # Se active_level=HIGH, linhas inativas=HIGH (não drenam)
        # Se active_level=LOW, linhas inativas=LOW (não drenam)
        if active_level == 'HIGH':
            row_inactive = GPIO.HIGH  # Não drena
        else:
            row_inactive = GPIO.LOW   # Não drena

        # Estado inativo para COLUNAS (anodos): oposto do active_level
        # Se active_level=HIGH, colunas inativas=LOW (não fornecem)
        # Se active_level=LOW, colunas inativas=HIGH (não fornecem)
        if active_level == 'HIGH':
            col_inactive = GPIO.LOW   # Não fornece
        else:
            col_inactive = GPIO.HIGH  # Não fornece

        # Configurar todas as linhas como OUTPUT (inicialmente desativadas)
        for row_pin in rows:
            GPIO.setup(row_pin, GPIO.OUT)
            GPIO.output(row_pin, row_inactive)

        # Configurar todas as colunas como OUTPUT (inicialmente desativadas)
        for col_pin in cols:
            GPIO.setup(col_pin, GPIO.OUT)
            GPIO.output(col_pin, col_inactive)

    except Exception as e:
        print(f"ERRO: Não foi possível configurar matriz de saída: {e}")
        cleanup_gpio()
        sys.exit(-5)


def setup_input_matrix(rows, cols, pull_mode):
    """
    Configura matriz de entrada (rows como OUTPUT, cols como INPUT com pull resistor).

    Args:
        rows (list): Lista de GPIOs para linhas (OUTPUT)
        cols (list): Lista de GPIOs para colunas (INPUT)
        pull_mode (str): 'UP' ou 'DOWN'

    Exit codes:
        -5: Erro ao configurar GPIO
    """
    setup_gpio()

    try:
        # Configurar linhas como OUTPUT (para escanear)
        for row_pin in rows:
            GPIO.setup(row_pin, GPIO.OUT)
            GPIO.output(row_pin, GPIO.LOW)  # Inicialmente LOW

        # Configurar colunas como INPUT com pull resistor
        pull = GPIO.PUD_UP if pull_mode == 'UP' else GPIO.PUD_DOWN
        for col_pin in cols:
            GPIO.setup(col_pin, GPIO.IN, pull_up_down=pull)

    except Exception as e:
        print(f"ERRO: Não foi possível configurar matriz de entrada: {e}")
        cleanup_gpio()
        sys.exit(-5)


def activate_position(row_pin, col_pin, active_level):
    """
    Ativa uma posição específica na matriz de saída.

    Para matriz de ânodo comum:
    - Coluna recebe active_level (fornece corrente)
    - Linha recebe OPOSTO (drena corrente)

    Args:
        row_pin (int): GPIO da linha (catodo/dreno)
        col_pin (int): GPIO da coluna (anodo/fonte)
        active_level (str): 'HIGH' ou 'LOW'
    """
    try:
        if active_level == 'HIGH':
            # Coluna HIGH (fornece), Linha LOW (drena)
            GPIO.output(col_pin, GPIO.HIGH)
            GPIO.output(row_pin, GPIO.LOW)
        else:
            # Coluna LOW (fornece), Linha HIGH (drena)
            GPIO.output(col_pin, GPIO.LOW)
            GPIO.output(row_pin, GPIO.HIGH)
    except Exception as e:
        print(f"ERRO: Não foi possível ativar posição: {e}")
        sys.exit(-5)


def deactivate_position(row_pin, col_pin, active_level):
    """
    Desativa uma posição específica na matriz de saída.

    Para matriz de ânodo comum:
    - Coluna recebe OPOSTO de active_level (não fornece)
    - Linha recebe active_level (não drena)

    Args:
        row_pin (int): GPIO da linha (catodo/dreno)
        col_pin (int): GPIO da coluna (anodo/fonte)
        active_level (str): 'HIGH' ou 'LOW'
    """
    try:
        if active_level == 'HIGH':
            # Coluna LOW (não fornece), Linha HIGH (não drena)
            GPIO.output(col_pin, GPIO.LOW)
            GPIO.output(row_pin, GPIO.HIGH)
        else:
            # Coluna HIGH (não fornece), Linha LOW (não drena)
            GPIO.output(col_pin, GPIO.HIGH)
            GPIO.output(row_pin, GPIO.LOW)
    except Exception as e:
        print(f"ERRO: Não foi possível desativar posição: {e}")
        sys.exit(-5)


def deactivate_all(rows, cols, active_level):
    """
    Desativa todas as posições da matriz de saída.

    Para matriz de ânodo comum:
    - Colunas no estado OPOSTO de active_level (não fornecem)
    - Linhas no estado active_level (não drenam)

    Args:
        rows (list): Lista de GPIOs para linhas (catodos/dreno)
        cols (list): Lista de GPIOs para colunas (anodos/fonte)
        active_level (str): 'HIGH' ou 'LOW'
    """
    try:
        # Estado inativo para linhas e colunas
        if active_level == 'HIGH':
            row_inactive = GPIO.HIGH  # Não drena
            col_inactive = GPIO.LOW   # Não fornece
        else:
            row_inactive = GPIO.LOW   # Não drena
            col_inactive = GPIO.HIGH  # Não fornece

        for row_pin in rows:
            GPIO.output(row_pin, row_inactive)

        for col_pin in cols:
            GPIO.output(col_pin, col_inactive)

    except Exception as e:
        print(f"ERRO: Não foi possível desativar matriz: {e}")
        sys.exit(-5)


def read_matrix(rows, cols, closed_state):
    """
    Lê estado completo da matriz de entrada.

    Args:
        rows (list): Lista de GPIOs para linhas
        cols (list): Lista de GPIOs para colunas
        closed_state (str): 'HIGH' ou 'LOW' (estado quando switch está fechado)

    Returns:
        list: Matriz 2D com estados ('on' ou 'off')

    Exit codes:
        -5: Erro ao ler GPIO
    """
    matrix_state = []

    try:
        for row_idx, row_pin in enumerate(rows):
            row_state = []

            # Ativar linha atual
            GPIO.output(row_pin, GPIO.HIGH)

            # Ler todas as colunas
            for col_idx, col_pin in enumerate(cols):
                col_value = GPIO.input(col_pin)

                # Determinar se está ativo
                if closed_state == 'HIGH':
                    is_active = (col_value == GPIO.HIGH)
                else:
                    is_active = (col_value == GPIO.LOW)

                row_state.append('on' if is_active else 'off')

            # Desativar linha
            GPIO.output(row_pin, GPIO.LOW)

            matrix_state.append(row_state)

        return matrix_state

    except Exception as e:
        print(f"ERRO: Não foi possível ler matriz de entrada: {e}")
        sys.exit(-5)
