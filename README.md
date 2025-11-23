# Sistema de acionamento e leitura de matrizes

## 📋 Visão Geral

Sistema de controle de acionamento e leitura de matrizes para Raspberry Pi.

**Scripts:**
- `matrix_write.py` - Script para acionamento de matriz de saída (ex: relés, LEDs)
- `matrix_read.py` - Script para leitura de uma matriz de entrada (ex: reed switches, teclado matricial)

---

## 🚀 Instalação

```bash
# Clonar repositório
git clone <repo-url>
cd matrix_control

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo de configuração a partir do template
cp config.yaml.example config.yaml
# Editar config.yaml com seus GPIOs específicos
nano config.yaml

# Configurar permissões GPIO
sudo usermod -a -G gpio $USER
# Logout e login novamente
```

---

## ⚙️ Arquivo de Configuração

**Template:** `config.yaml.example` (copie para `config.yaml` e edite conforme seu hardware)

**Localização:** `config.yaml` (mesmo diretório dos scripts)

**Importante:** O arquivo `config.yaml` não é versionado. Você deve criá-lo a partir do template:
```bash
cp config.yaml.example config.yaml
nano config.yaml  # Ajuste os GPIOs conforme seu hardware
```

**Exemplo de configuração:**

```yaml
# config.yaml

output:
  # Matriz de acionamento (relés, LEDs, etc)
  pinout:
    rows: [26, 19, 13]      # GPIO BCM numbering
    cols: [22, 27, 17]
    active_level: LOW       # HIGH ou LOW (lógica do relé/dispositivo)

input:
  # Matriz de entrada (reed switches, teclado matricial, etc)
  input_matrix:
    rows: [21, 20, 16]      # GPIO BCM numbering (configurados como INPUT)
    cols: [12, 25, 24]      # GPIO BCM numbering (configurados como OUTPUT)
    pull_mode: DOWN         # DOWN ou UP
    closed_state: HIGH      # HIGH = Switch NA, LOW = Switch NC

  # Intervalo de atualização do padrão do modo monitor (segundos)
  monitor_interval: 0.5
```

---

## 🔓 Script 1: matrix_write.py

Controla ativação da matriz de saída.

### **Sintaxe**

```bash
# Ativar posição por tempo determinado
python matrix_write.py <posição> <duração>

# Resetar (desativar tudo)
python matrix_write.py reset
```

### **Parâmetros**

| Parâmetro | Tipo   | Descrição                                                                                                                      |
| --------- | ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `posição` | string | Posição a ser ativada. Formato: A1 (Coluna A Linha 1) ou 4 (quarta posição, numa matrix 3x3 seria a posição B1)              |
| `duração` | float  | Tempo em segundos (obrigatório). Range: 0.5s até 600s (10 minutos)                                                            |
| `reset`   | string | Comando especial para desativar todas as posições                                                                             |

### **Comportamento**

**Ativação:**
- Posição é ativada pelo tempo especificado
- Desativa automaticamente após tempo especificado
- Range de duração: 0.5s até 600s (10 minutos)
- Script aguarda até desativação automática

### **Exemplos**

```bash
# Ativa posição A2 por 2 segundos
python matrix_write.py A2 2.0

# Ativa posição 4 (B1 numa matriz 3x3) por 5 segundos
python matrix_write.py 4 5.0

# Resetar sistema (desativar tudo)
python matrix_write.py reset
```

### **Saída**

```bash
# Sucesso
Posição A2: ATIVADA por 2.0s

# Reset
Sistema resetado: todas as posições desativadas

# Erro - duração não especificada
ERRO: Duração em segundos é obrigatória
Uso: python matrix_write.py <posição> <duração>
Exemplo: python matrix_write.py A1 2.0
```

### **Exit Codes**

- `0` - Sucesso
- `-1` - Erro genérico
- `-2` - Posição inválida
- `-4` - Duração inválida
- `-5` - Erro de hardware (GPIO)
- `-6` - Arquivo de configuração não encontrado

---

## 📡 Script 2: matrix_read.py

Lê a matriz de entrada e retorna o resultado. Também pode ser utilizada para leitura contínua.

### **Sintaxe**

```bash
python matrix_read.py [--interval intervalo]
```

### **Parâmetros**

| Parâmetro    | Tipo  | Descrição                                                                                                              |
| ------------ | ----- | ---------------------------------------------------------------------------------------------------------------------- |
| `--interval` | float | Habilita modo contínuo com intervalo especificado (em segundos). Sem este parâmetro, faz apenas uma leitura única. |
### **Comportamento**

#### Leitura única

1. Faz uma leitura instantânea da matriz
2. Retorna o estado em formato JSON
3. Script finaliza imediatamente após a leitura

#### Leitura contínua

1. Faz a leitura a cada `intervalo` segundos
2. `Ctrl+C` para sair

### **Exemplos**

```bash
# Retorna o estado atual da matriz
python matrix_read.py

# Leitura com atualização a cada 1 segundo
python matrix_read.py --interval 1.0

# Leitura rápida (0.2s)
python matrix_read.py --interval 0.2
```

### **Saída**

#### Leitura única
```json
{
   "matrix":[
      ["on", "off", "off"],
      ["off", "off", "on"],
      ["off", "on", "off"]
   ]
}
```

#### Leitura contínua

```
┌────────────────────────────────────────────┐
│   Matrix Monitor                           │
│   Update interval: 0.5s | Ctrl+C to exit   │
├────────────────────────────────────────────┤
│     A      B      C                        │
│ 1  [X]    [ ]    [X]                       │
│ 2  [ ]    [X]    [ ]                       │
│ 3  [X]    [ ]    [X]                       │
└────────────────────────────────────────────┘
```

**Legenda:**
- `[X]` = Ativado
- `[ ]` = Desativado

### **Exit Codes**

- `0` - Saída normal (Ctrl+C)
- `-5` - Erro crítico ao ler sensores
- `-6` - Arquivo de configuração não encontrado

---

## 📖 Uso Típico

### **Terminal 1 Leitura da matriz de entrada**

```bash
# Iniciar leitura em um terminal
python matrix_read.py --interval 1.0

# Tela fica atualizando continuamente
# Mostra mudanças de estado em tempo real
```

### **Terminal 2: Controle da matriz de saída**

```bash
# Em outro terminal, controlar a matriz de saída
python matrix_write.py A2 2.0
python matrix_write.py B1 5.0
python matrix_write.py C3 1.5
```

---
## 🚨 Tratamento de Erros

### **Mensagens de Erro - matrix_write.py**

| Mensagem                                 | Causa                              | Solução                                                |
| ---------------------------------------- | ---------------------------------- | ------------------------------------------------------ |
| `Posição X inválida`                     | Posição fora dos limites da matriz | Usar posição válida                                    |
| `Duração inválida`                       | Valor fora de 0.5-600s             | Ajustar duração                                        |
| `Duração em segundos é obrigatória`      | Não especificou duração            | Adicionar tempo: `python matrix_write.py A1 2.0`       |
| `Erro ao acessar GPIO`                   | Permissões ou hardware             | Verificar permissões e conexões                        |
| `Arquivo de configuração não encontrado` | Falta config.yaml                  | Criar arquivo de configuração                          |

### **Mensagens de Erro - matrix_read.py**

| Mensagem                                 | Causa                 | Solução                       |
| ---------------------------------------- | --------------------- | ----------------------------- |
| `Erro ao ler posição X`                  | Sensor desconectado   | Verificar conexões físicas    |
| `GPIO não disponível`                    | Outro processo usando | Encerrar outros processos     |
| `Arquivo de configuração não encontrado` | Falta config.yaml     | Criar arquivo de configuração |

---

## 🛠️ Troubleshooting

### **Problema: Scripts não encontram config.yaml**

```bash
# Verificar se está no diretório correto
ls config.yaml

# Ou especificar caminho absoluto no script
# Editar primeira linha dos scripts Python:
CONFIG_PATH = '/caminho/completo/para/config.yaml'
```

### **Problema: saída ativa mas não desativa automaticamente**

```bash
# Verificar se script ficou em background
ps aux | grep matrix_write.py

# Matar processos órfãos
pkill -f matrix_write.py
```

---

## 📦 Estrutura do Projeto

```
matrix_control/
├── .gitignore               # Arquivos ignorados pelo Git
├── config.yaml.example      # Template de configuração
├── config.yaml              # Configuração do hardware (criar localmente)
├── config_loader.py         # Módulo de carregamento de configuração
├── gpio_manager.py          # Módulo de gerenciamento de GPIO
├── matrix_utils.py          # Módulo de funções auxiliares
├── matrix_write.py          # Script de controle de saída
├── matrix_read.py           # Script de leitura de entrada
└── requirements.txt         # Dependências Python
```

---

## 📝 Notas Técnicas

### **Independência dos Scripts**

- **matrix_write.py**: Não precisa do `matrix_read.py` rodando
- **matrix_read.py**: Não precisa do `matrix_write.py` rodando
- Ambos podem rodar simultaneamente sem conflito
- GPIO de leitura != GPIO de escrita (matrizes separadas)

### **Arquitetura das Matrizes**

**Matriz de Saída (output):**
- Linhas (rows): Configuradas como OUTPUT
- Colunas (cols): Configuradas como OUTPUT
- Ativação: Uma linha e uma coluna são ativadas simultaneamente para acionar a posição

**Matriz de Entrada (input):**
- Linhas (rows): Configuradas como INPUT com pull resistor
- Colunas (cols): Configuradas como OUTPUT para varredura
- Leitura: Cada coluna é ativada sequencialmente e todas as linhas são lidas

### **Limitação de Acionamento Simultâneo**

Arquitetura em matriz permite apenas **1 posição ativada por vez**:

```bash
# Correto - aguarda desativação antes de ativar próxima
python matrix_write.py A2 2.0
python matrix_write.py A3 2.0

# Problemático - ativa em background simultaneamente
python matrix_write.py A2 10.0 &
python matrix_write.py A3 10.0 &  # Tenta ativar a segunda posição simultaneamente!
```

**Por quê?** Matriz compartilha linhas/colunas. Ativar duas posições simultaneamente causa interferência.

---

## 🔐 Permissões

```bash
# Adicionar usuário ao grupo gpio (executar UMA vez)
sudo usermod -a -G gpio $USER

# IMPORTANTE: Logout e login para aplicar

# Verificar
groups | grep gpio

# Se não funcionar, executar scripts com sudo (não recomendado)
sudo python matrix_write.py A2 2.0
```

---

## 🧪 Testes

### **Teste Manual Básico**

```bash
# Terminal 1
python matrix_read.py --interval 0.5

# Terminal 2
python matrix_write.py A2 3.0  # Ativa a posição A2 por 3 segundos
python matrix_write.py B1 2.0  # Ativa a posição B1 por 2 segundos
```

### **Teste de Todas as Posições**

```bash
# Terminal 1
python matrix_read.py

# Terminal 2
for i in {1..9}; do
    python matrix_write.py $i 1.0
    sleep 0.5
done
```

---

## 📄 Dependências

**requirements.txt**

```
RPi.GPIO>=0.7.1
PyYAML>=6.0
```

Instalação:
```bash
pip install -r requirements.txt
```
