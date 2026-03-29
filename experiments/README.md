# Experiments

Este diretório contém apenas artefatos experimentais externos ao core.

## Estrutura mínima

- `configs/`: protocolos experimentais versionados
- `scenarios/`: cenários versionados
- `runs/`: saídas persistidas de execuções
- `reports/`: relatórios gerados a partir das runs
- `notebooks/`: análises exploratórias
- `figures/`: figuras exportadas

## Regras

- `experiments/` não substitui `core/experiments`
- protocolo e cenário continuam modelados no core
- esta pasta guarda apenas definição externa e artefatos
- benchmark não é demo
- demo não é teste
- execução deve sempre persistir em `experiments/runs/<run_id>/`

## Scripts mínimos

### Exportar visão consolidada das métricas

```bash
python scripts/export_metrics.py
```

### Comparar runs específicas
```bash
python scripts/compare_runs.py run_a run_b
```

---

### **Arquivo novo**
`experiments/configs/pbvs_with_avoidance_protocol.yaml`

#### Conteúdo completo
```yaml
name: pbvs_with_avoidance_protocol
repetitions: 3
seeds: [101, 102, 103]
compared_methods:
  - pbvs_baseline
  - pbvs_with_avoidance
resolved_config:
  app:
    use_case: run_pbvs_with_avoidance
  scenario_name: person_in_workspace
  backend_name: coppeliasim
  planning:
    duration: 2.0
  visual_servoing:
    enabled: true
    kind: pbvs
    gain: 0.9
  obstacle_avoidance:
    enabled: true
    kind: cuckoo_search
    clearance_m: 0.20
