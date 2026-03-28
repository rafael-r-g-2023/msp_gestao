# MULTISERVICE PRIME - Sistema de Gestão

## 📌 Visão Geral

Sistema desenvolvido para gestão completa da empresa MULTISERVICE PRIME, incluindo:

- Serviços
- Financeiro
- Orçamentos
- Funcionários (RH)
- Veículos (Frota)
- Clientes

---

## 🧩 Estrutura do Sistema

### 1. CLIENTES
- Cadastro de clientes
- Histórico de serviços
- Relacionamento com OS e Orçamentos

### 2. ORÇAMENTOS
- Criação de orçamento
- Itens do orçamento
- Geração de PDF
- Aprovação do cliente
- Conversão para Ordem de Serviço

### 3. SERVIÇOS
- Ordem de Serviço (OS)
- Itens da OS
- Tipos de serviço
- Status (agendado / executado / cancelado)

### 4. FINANCEIRO
- Receitas
- Despesas
- Categorias
- Integração com OS
- Dashboard

### 5. FUNCIONÁRIOS (RH)
- Cadastro de funcionários
- Custo por dia
- Vínculo com OS
- (Futuro) cursos e certificações

### 6. VEÍCULOS (FROTA)
- Cadastro de veículos
- Consumo (km/l)
- KM rodado
- Custo por KM
- (Futuro) manutenção da frota

---

## 🔄 Fluxo do Sistema

CLIENTE  
↓  
ORÇAMENTO  
↓  
APROVAÇÃO  
↓  
ORDEM DE SERVIÇO  
↓  
EXECUÇÃO  
↓  
FINANCEIRO  
↓  
DASHBOARD  

---

## 🔗 Integrações

### Ordem de Serviço
- Cliente
- Funcionários
- Veículo
- Itens de serviço
- KM rodado
- Combustível

### Financeiro
- Receita gerada automaticamente pela OS executada
- Cálculo de custos:
  - Funcionários
  - KM
  - Despesas gerais

---

## 🚀 Evoluções Futuras

- Módulo completo de Orçamentos
- Controle de cursos (RH)
- Relatórios avançados
- Indicadores de desempenho
- Controle de manutenção de veículos
