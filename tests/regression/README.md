# Regression tests

Esta pasta contém testes de regressão numérica e algorítmica para os subsistemas
científicos do framework.

## Objetivo

Detectar mudanças silenciosas em:

- planejamento
- controle
- servo visual
- avoidance
- métricas científicas

## Regras

- os cenários devem ser pequenos e determinísticos
- não depender de inspeção visual
- não depender de cena manual
- não depender de backend externo
- os valores de referência devem ser explícitos

## Escopo inicial

- trajetória quíntica articular
- controladores PI / PD / PD adaptativo
- PBVS
- composição PBVS + avoidance
- métricas numéricas associadas
