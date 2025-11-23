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

    Inicializa todos os pinos no estado desativado (oposto do active_level).

    Args:
        rows (list): Lista de GPIOs para linhas
        cols (list): Lista de GPIOs para colunas
        active_level (str): 'HIGH' ou 'LOW' - nível para ativar posições

    Exit codes:
        -5: Erro ao configurar GPIO
    """
    setup_gpio()

    try:
        # Estado inativo (desativado): oposto do active_level
        # active_level=HIGH → inativo=LOW
        # active_level=LOW → inativo=HIGH
        if active_level == 'HIGH':
            inactive_state = GPIO.LOW
        else:
            inactive_state = GPIO.HIGH

        # Configurar todas as linhas como OUTPUT (inicialmente desativadas)
        for row_pin in rows:
            GPIO.setup(row_pin, GPIO.OUT)
            GPIO.output(row_pin, inactive_state)

        # Configurar todas as colunas como OUTPUT (inicialmente desativadas)
        for col_pin in cols:
            GPIO.setup(col_pin, GPIO.OUT)
            GPIO.output(col_pin, inactive_state)

    except Exception as e:
        print(f"ERRO: Não foi possível configurar matriz de saída: {e}")
        cleanup_gpio()
        sys.exit(-5)


def setup_input_matrix(rows, cols, pull_mode):
    """
    Configura matriz de entrada (rows como INPUT com pull resistor, cols como OUTPUT).

    Args:
        rows (list): Lista de GPIOs para linhas (INPUT)
        cols (list): Lista de GPIOs para colunas (OUTPUT)
        pull_mode (str): 'UP' ou 'DOWN'

    Exit codes:
        -5: Erro ao configurar GPIO
    """
    setup_gpio()

    try:
        # Configurar colunas como OUTPUT (para escanear)
        for col_pin in cols:
            GPIO.setup(col_pin, GPIO.OUT)
            GPIO.output(col_pin, GPIO.LOW)  # Inicialmente LOW

        # Configurar linhas como INPUT com pull resistor
        pull = GPIO.PUD_UP if pull_mode == 'UP' else GPIO.PUD_DOWN
        for row_pin in rows:
            GPIO.setup(row_pin, GPIO.IN, pull_up_down=pull)

    except Exception as e:
        print(f"ERRO: Não foi possível configurar matriz de entrada: {e}")
        cleanup_gpio()
        sys.exit(-5)


def activate_position(row_pin, col_pin, active_level):
    """
    Ativa uma posição específica na matriz de saída.

    Define row e col para o active_level configurado.

    Args:
        row_pin (int): GPIO da linha
        col_pin (int): GPIO da coluna
        active_level (str): 'HIGH' ou 'LOW'
    """
    try:
        if active_level == 'HIGH':
            # Ativar: ambos HIGH
            GPIO.output(col_pin, GPIO.HIGH)
            GPIO.output(row_pin, GPIO.HIGH)
        else:
            # Ativar: ambos LOW
            GPIO.output(col_pin, GPIO.LOW)
            GPIO.output(row_pin, GPIO.LOW)
    except Exception as e:
        print(f"ERRO: Não foi possível ativar posição: {e}")
        sys.exit(-5)


def deactivate_position(row_pin, col_pin, active_level):
    """
    Desativa uma posição específica na matriz de saída.

    Define row e col para o oposto do active_level configurado.

    Args:
        row_pin (int): GPIO da linha
        col_pin (int): GPIO da coluna
        active_level (str): 'HIGH' ou 'LOW'
    """
    try:
        if active_level == 'HIGH':
            # Desativar: ambos LOW (oposto de HIGH)
            GPIO.output(col_pin, GPIO.LOW)
            GPIO.output(row_pin, GPIO.LOW)
        else:
            # Desativar: ambos HIGH (oposto de LOW)
            GPIO.output(col_pin, GPIO.HIGH)
            GPIO.output(row_pin, GPIO.HIGH)
    except Exception as e:
        print(f"ERRO: Não foi possível desativar posição: {e}")
        sys.exit(-5)


def deactivate_all(rows, cols, active_level):
    """
    Desativa todas as posições da matriz de saída.

    Define todos os pinos (rows e cols) para o oposto do active_level.

    Args:
        rows (list): Lista de GPIOs para linhas
        cols (list): Lista de GPIOs para colunas
        active_level (str): 'HIGH' ou 'LOW'
    """
    try:
        # Estado inativo: oposto do active_level
        # active_level=HIGH → inativo=LOW
        # active_level=LOW → inativo=HIGH
        if active_level == 'HIGH':
            inactive_state = GPIO.LOW
        else:
            inactive_state = GPIO.HIGH

        for row_pin in rows:
            GPIO.output(row_pin, inactive_state)

        for col_pin in cols:
            GPIO.output(col_pin, inactive_state)

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
        for col_idx, col_pin in enumerate(cols):
            col_state = []

            # Ativar coluna atual
            GPIO.output(col_pin, GPIO.HIGH)

            # Ler todas as linhas
            for row_idx, row_pin in enumerate(rows):
                row_value = GPIO.input(row_pin)

                # Determinar se está ativo
                if closed_state == 'HIGH':
                    is_active = (row_value == GPIO.HIGH)
                else:
                    is_active = (row_value == GPIO.LOW)

                col_state.append('on' if is_active else 'off')

            # Desativar coluna
            GPIO.output(col_pin, GPIO.LOW)
            matrix_state.append(col_state)

        matrix_reverse = [[matrix_state[j][i] for j in range(len(matrix_state))] for i in range(len(matrix_state[0]))]
        return matrix_reverse

    except Exception as e:
        print(f"ERRO: Não foi possível ler matriz de entrada: {e}")
        sys.exit(-5)
