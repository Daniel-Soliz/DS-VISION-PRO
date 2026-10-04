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

## Versão atual

### v0.4
- Dashboard desktop escuro.
- Seleção visual independente de M5, M15 e M1.
- Preview com **overlay de calibração**, mostrando quais candles o robô reconheceu.
- Relógio para o próximo minuto como apoio visual de timing.
- Catálogo interno de padrões.
- Histórico de sinais.
- Alerta por voz.
- Journal CSV.
- Motor de confluência M5/M15/M1.
- Bloqueio de entrada quando M5 e M15 entram em conflito.

## O que o motor analisa

### Candlesticks
Doji, Dragonfly Doji, Gravestone Doji, Spinning Top, Martelo, Martelo Invertido, Homem Enforcado, Estrela Cadente, Engolfo de Alta/Baixa, Harami de Alta/Baixa, Piercing Line, Dark Cloud Cover, Morning Star, Evening Star, Três Soldados Brancos, Três Corvos Negros, Marubozu, Tweezer Top/Bottom, Bullish/Bearish Kicker, Three Inside Up/Down e Three Outside Up/Down.

### Estrutura
Suporte, resistência, pivôs, rompimento, falso rompimento/rejeição, pullback, LTA, LTB, tendência curta, momentum e proximidade de zonas contrárias.

### Confluência profissional
O DS VISION PRO não transforma um único padrão em entrada. Cada leitura soma e subtrai pontos. Se M5/M15 conflitarem ou a vantagem for pequena, o resultado é **AGUARDAR**.

O número de força exibido é **score técnico de confluência**, não probabilidade garantida de acerto.

## Como usar

1. Instale Python 3.11+ no Windows.
2. Execute `INSTALL.bat`.
3. Execute `RUN.bat`.
4. Abra a IQ Option no PC.
5. Deixe os gráficos que deseja analisar visíveis.
6. No DS VISION PRO, selecione a região M5.
7. Selecione a região M15.
8. Opcionalmente selecione M1 para melhorar o timing de 60 segundos.
9. Confira no preview se os retângulos de calibração estão cobrindo corretamente as velas.
10. Clique em **INICIAR LEITURA**.

Selecione somente a área de velas. Evite menus, lista de ativos, botões, textos e eixo de preço.

## Gerar executável

Execute `BUILD_EXE.bat`. A versão local será criada em:

`dist/DS_VISION_PRO/DS_VISION_PRO.exe`

### Windows Smart App Control / SmartScreen

O build do GitHub ainda é um aplicativo **não assinado digitalmente**. Por isso o Windows pode bloquear o EXE baixado da internet mesmo quando o código foi gerado pelo próprio repositório.

Para os testes iniciais, a opção recomendada é **gerar o aplicativo localmente com `BUILD_EXE.bat`**, em vez de desligar o Smart App Control.

O workflow do GitHub também publica um arquivo `SHA256SUM.txt` junto do build para conferência de integridade.

Para distribuição pública sem esse tipo de alerta, a etapa correta é assinar o executável com um certificado de assinatura de código confiável.

## Estrutura

```text
app.py
dsvision/
  catalog.py
  confluence.py
  journal.py
  models.py
  patterns.py
  structure.py
  timing.py
  vision.py
config/default.json
docs/PATTERNS.md
tests/test_engine.py
```

## Roadmap

- Calibrar o reconhecimento para capturas reais da IQ Option.
- Adicionar resultados WIN/LOSS ao journal e medir desempenho real por padrão.
- Ranking de padrões por ativo e timeframe.
- Zonas de suporte/resistência por múltiplos toques.
- Detector de consolidação e mercado lateral.
- Filtro de volatilidade.
- Painel de estatísticas e taxa histórica de acerto do próprio DS.
- Empacotamento final e instalador Windows.

## Limites importantes

Leitura por tela é sensível a zoom, tema, sobreposição de textos e mudanças visuais da plataforma. A validação em conta de demonstração e o journal de resultados fazem parte do projeto. Não existe previsão perfeita da próxima vela.

## Usar como aplicativo com dois cliques

Depois de instalar as dependências, gere o aplicativo localmente com BUILD_EXE.bat. O executável ficará em:

`dist/DS_VISION_PRO/DS_VISION_PRO.exe`

Em seguida, execute CRIAR_ATALHO.bat para criar **DS VISION PRO** na Área de Trabalho. Depois disso, basta abrir pelo atalho como qualquer outro aplicativo do Windows.

Se o Windows bloquear os arquivos .bat baixados, os mesmos comandos podem ser executados manualmente no PowerShell. Para este computador, o comando correto é `python`, não `py`.
\n## Correção v0.4: configuração do aplicativo\n\nO executável não depende mais de `config/default.json` dentro da pasta do PyInstaller. As configurações e o histórico são gravados em `%LOCALAPPDATA%\\DS VISION PRO`, permitindo abrir o aplicativo pelo EXE/atalho sem erro de arquivo ausente.\n