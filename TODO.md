# TODO - Sistema de Controle de Matrizes

## 📋 Lista de Tarefas (em ordem de execução)

### 1. Configuração Inicial do Projeto
- [ ] 1.1. Criar arquivo `requirements.txt` com dependências Python
- [ ] 1.2. Criar arquivo `config.yaml` de exemplo com configurações padrão

### 2. Módulos Compartilhados
- [ ] 2.1. Criar módulo `config_loader.py` - Carregamento e validação do config.yaml
- [ ] 2.2. Criar módulo `matrix_utils.py` - Funções auxiliares (conversão de posições, validações)
- [ ] 2.3. Criar módulo `gpio_manager.py` - Gerenciamento de GPIO (setup, cleanup)

### 3. Script matrix_write.py
- [ ] 3.1. Implementar parsing de argumentos da linha de comando
- [ ] 3.2. Implementar validação de posições (formato A1 ou numérico)
- [ ] 3.3. Implementar validação de duração (0.5s a 600s)
- [ ] 3.4. Implementar lógica de ativação/desativação de posição
- [ ] 3.5. Implementar detecção e tratamento de conflitos
- [ ] 3.6. Implementar timeout automático para duração definida
- [ ] 3.7. Implementar safety_timeout do config.yaml
- [ ] 3.8. Implementar force_off_on_conflict
- [ ] 3.9. Implementar exit codes específicos (-1 a -6)
- [ ] 3.10. Implementar mensagens de saída conforme especificação

### 4. Script matrix_read.py
- [ ] 4.1. Implementar parsing de argumentos (--interval)
- [ ] 4.2. Implementar leitura única da matriz
- [ ] 4.3. Implementar saída JSON para leitura única
- [ ] 4.4. Implementar modo contínuo (monitor)
- [ ] 4.5. Implementar display visual com emojis (🟢/🔴)
- [ ] 4.6. Implementar atualização em tempo real (limpar tela)
- [ ] 4.7. Implementar tratamento de Ctrl+C para saída limpa
- [ ] 4.8. Implementar exit codes específicos (0, -5, -6)
- [ ] 4.9. Suporte a matrizes de tamanho configurável

### 5. Tratamento de Erros e Robustez
- [ ] 5.1. Implementar tratamento de GPIO ocupado
- [ ] 5.2. Implementar tratamento de permissões insuficientes
- [ ] 5.3. Implementar cleanup de GPIO em caso de erro
- [ ] 5.4. Implementar validação completa do config.yaml
- [ ] 5.5. Implementar mensagens de erro amigáveis

### 6. Testes
- [ ] 6.1. Testar matrix_write.py com diferentes posições
- [ ] 6.2. Testar matrix_write.py com durações variadas
- [ ] 6.3. Testar conflitos de posições
- [ ] 6.4. Testar safety_timeout
- [ ] 6.5. Testar matrix_read.py em modo único
- [ ] 6.6. Testar matrix_read.py em modo contínuo
- [ ] 6.7. Testar ambos os scripts rodando simultaneamente
- [ ] 6.8. Testar com diferentes tamanhos de matriz
- [ ] 6.9. Testar todos os exit codes
- [ ] 6.10. Testar tratamento de erros

### 7. Documentação e Finalização
- [ ] 7.1. Adicionar comentários no código
- [ ] 7.2. Verificar conformidade com README.md
- [ ] 7.3. Criar script de teste automatizado (opcional)
- [ ] 7.4. Validar permissões GPIO necessárias

---

## 📝 Notas de Implementação

### Decisões Técnicas
- **Numeração BCM**: Usar GPIO.BCM para numeração de pinos
- **Matrizes configuráveis**: Suportar qualquer tamanho NxM (não apenas 3x3)
- **Thread-safety**: Considerar uso de locks se necessário
- **Cleanup**: Garantir GPIO.cleanup() sempre executado

### Formato de Posições
- **Alfanumérico**: A1, B2, C3 (Coluna + Linha)
- **Numérico**: 1-9 para 3x3 (ordem: A1=1, A2=2, A3=3, B1=4, etc)
- **Cálculo**: posição_numérica = (linha * num_colunas) + coluna + 1

### Prioridades
1. ✅ Configuração e estrutura base
2. ✅ Funcionalidades core
3. ✅ Tratamento de erros
4. ✅ Testes
5. ✅ Documentação

---

## 🎯 Status Atual
**Fase**: Início do projeto
**Próximo passo**: Criar requirements.txt e config.yaml
