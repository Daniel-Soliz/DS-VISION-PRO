# DS VISION PRO

Assistente desktop de análise técnica multi-timeframe criado para trabalhar **ao lado da IQ Option no Windows**.

> Projeto independente. Não é afiliado, endossado ou operado pela IQ Option.

## Foco inicial

- Contexto principal: **M5 e M15**
- Expiração operacional configurada: **60 segundos**
- Confirmação micro opcional: **M1**
- Saída: **ALTA**, **BAIXA** ou **AGUARDAR**
- Sem execução automática de ordens nesta versão
- Sem solicitar login/senha da corretora

## O que o motor analisa

### Candlesticks
Doji, Dragonfly Doji, Gravestone Doji, Spinning Top, Martelo, Martelo Invertido, Homem Enforcado, Estrela Cadente, Engolfo de Alta/Baixa, Harami de Alta/Baixa, Piercing Line, Dark Cloud Cover, Morning Star, Evening Star, Três Soldados Brancos, Três Corvos Negros e Marubozu.

### Estrutura
Suporte, resistência, pivôs, rompimento, falso rompimento/rejeição, pullback, LTA, LTB, tendência curta, momentum e volatilidade.

### Confluência profissional
O DS VISION PRO não transforma um único padrão em entrada. Cada leitura soma e subtrai pontos. Se M5/M15 conflitarem ou a vantagem for pequena, o resultado é **AGUARDAR**.

O número de força exibido é **score técnico de confluência**, não probabilidade garantida de acerto.

## Como usar

1. Instale Python 3.11+ no Windows.
2. Execute `INSTALL.bat`.
3. Execute `RUN.bat`.
4. Abra a IQ Option no PC.
5. Deixe um gráfico M5 e/ou M15 visível.
6. No DS VISION PRO, selecione a região do gráfico correspondente.
7. Opcionalmente selecione um gráfico M1 para melhorar o timing de 60 segundos.
8. Clique em **INICIAR LEITURA**.

Selecione somente a área de velas. Evite menus, lista de ativos, botões, textos e eixo de preço.

## Gerar executável

Execute `BUILD_EXE.bat`. O EXE será criado em `dist/DS_VISION_PRO.exe`.

## Estrutura

```text
app.py
dsvision/
  models.py
  vision.py
  patterns.py
  structure.py
  confluence.py
  journal.py
config/default.json
docs/PATTERNS.md
tests/test_engine.py
```

## Limites importantes

Leitura por tela é sensível a zoom, tema, sobreposição de textos e mudanças visuais da plataforma. A validação em conta de demonstração e o journal de resultados fazem parte do projeto. Não existe previsão perfeita da próxima vela.
