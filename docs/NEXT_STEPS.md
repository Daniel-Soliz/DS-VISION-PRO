# Próximos passos — DS VISION PRO

## Fase 1 — Calibração IQ Option
Objetivo: garantir que o detector visual reconheça corretamente as velas reais do usuário.

Checklist:
- M5 com 20–40 candles visíveis.
- M15 com 20–40 candles visíveis.
- M1 opcional.
- Confirmar overlay nos corpos e pavios.
- Ajustar HSV, largura e filtros caso textos/ícones sejam confundidos com candles.

## Fase 2 — Validação em demo
Objetivo: parar de avaliar apenas sensação visual e começar a medir.

- Registrar timestamp, direção, força, M5, M15 e M1.
- Marcar WIN/LOSS/DRAW.
- Separar desempenho por padrão.
- Separar desempenho por contexto: suporte, resistência, LTA, LTB, rompimento e pullback.
- Medir amostra mínima antes de alterar pesos.

## Fase 3 — Estrutura avançada
- Suportes e resistências por múltiplos toques.
- Swing highs / swing lows.
- HH, HL, LH, LL.
- Consolidação/range.
- Breakout + reteste.
- Exaustão após sequência longa.
- Filtro de volatilidade.

## Fase 4 — Score adaptativo
Os pesos deixam de ser apenas definidos manualmente e passam a ser comparados com o journal real do DS. O software continua mostrando score técnico, e estatísticas históricas aparecem separadamente.

## Fase 5 — Distribuição Windows
- Build EXE.
- Instalador.
- Configurações persistentes.
- Atualização de versão.
- Backup/exportação do journal.

A execução automática de ordens não faz parte das primeiras fases. Primeiro o motor precisa ser validado em demo.
