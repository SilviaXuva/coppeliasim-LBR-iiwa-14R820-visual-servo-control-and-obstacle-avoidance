# Tests

Este diretório contém a suíte automatizada do framework.

## Estrutura

- `tests/unit/`: corretude local de módulos isolados
- `tests/integration/`: integração real entre camadas, composição e adapters
- `tests/contract/`: conformidade de interfaces/ports/adapters
- `tests/regression/`: estabilidade numérica e algorítmica dos subsistemas científicos
- `tests/fixtures/`: dublês e utilitários compartilhados

## Regra importante

- teste unitário não substitui regressão
- regressão não substitui benchmark
- benchmark não substitui experimento científico

## Escopo mínimo de regressão

A suíte de regressão deve cobrir pelo menos:

- planejamento
- controle
- visual servoing
- avoidance
- métricas científicas críticas
