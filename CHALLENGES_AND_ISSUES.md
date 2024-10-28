# 27/10/2024 - Problema de Classificação de Frases Grandes e Escalabilidade de Rótulos

## Contexto

O modelo que estamos desenvolvendo foi inicialmente planejado para classificar comandos simples e diretos, como "abra o navegador" ou "verifique os dados do treino". Com o tempo, conforme adicionamos mais dados e rótulos, percebemos que o nível de complexidade das frases começou a aumentar, e surgiram novos desafios no tratamento e classificação correta das frases.

O objetivo inicial era trabalhar com **apenas 8 rótulos**, categorizando palavras em classes como `Comando`, `Entidade`, `Tempo`, entre outros. Entretanto, frases mais complexas e maiores, como:

> "Oi, tenho esses dados aqui, pode verificar para mim hoje?"

Estão causando problemas de ambiguidade e dificuldade na classificação correta.

## Problemas Enfrentados

1. **Frases Longas com Poucos Rótulos**:
    - Ao trabalhar com frases longas e complexas, o número limitado de rótulos torna difícil a classificação precisa de todas as palavras.
    - Em frases pequenas, como "abra o navegador", o modelo consegue classificar corretamente usando apenas 8 rótulos. No entanto, à medida que as frases crescem em tamanho e complexidade, surgem ambiguidades.

2. **Ambiguidade e Classificação Incorreta**:
    - Com poucos rótulos, enfrentamos ambiguidade em certas palavras. Por exemplo, palavras que deveriam pertencer a uma classe `Comando` podem ser erroneamente classificadas em outras categorias.
    - Mesmo que o modelo seja treinado para lidar com essas classificações, a quantidade limitada de rótulos não é suficiente para cobrir a variedade e a nuance das frases maiores.

3. **Escalabilidade dos Dados**:
    - Com a introdução de mais rótulos para melhorar a classificação, enfrentamos o problema da **escalabilidade dos dados**. Uma única frase pode gerar um número grande de classificações, especialmente se começarmos a introduzir subcategorias ou mais granularidade.
    - Esse aumento de classes e rótulos causa um crescimento exponencial no tamanho do dataset e dificulta o gerenciamento das classificações.

## Solução Proposta

### 1. **Divisão Modular de Rótulos**

- **Estruturar os rótulos em categorias e subcategorias**. Ao invés de adicionar rótulos de maneira ad-hoc, vamos organizar em grupos hierárquicos:
    - **Comando**: Para ações diretas.
    - **Entidade**: Pessoas, objetos, ou organizações.
    - **Localização**:
        - **Localização_Geral**: Para estados, países e grandes regiões.
        - **Localização_Especifica**: Cidades, bairros, ou locais específicos.
    - **Tempo**: Referências temporais.
    - **Qualidade**: Para descrições ou qualificações (ex: "melhores").
    - **Estado**: Situações ou condições.

- **Por que isso é útil?**
    - Ao organizar os rótulos de forma modular e hierárquica, podemos gerenciar melhor a complexidade das frases grandes e evitar ambiguidades, limitando os rótulos a um escopo claro e bem definido.

### 2. **Limitar o Crescimento Inicial de Rótulos**

- Ao invés de expandir os rótulos para todas as possíveis categorias de uma só vez, a estratégia será introduzir novos rótulos de maneira incremental.
- **Fases de treinamento**:
    - Primeiramente, focamos nos rótulos essenciais, como `Comando`, `Entidade` e `Tempo`.
    - Somente após estabilizarmos a classificação desses rótulos, começamos a introduzir mais granularidade com subcategorias.

### 3. **Foco em Frases Simples e Diretas**

- Como o modelo foi projetado inicialmente para comandos simples, podemos **retornar ao foco original**, limitando a complexidade das frases no início do treinamento. Isso evita que o modelo se perca em nuances desnecessárias de frases complexas.
- Frases curtas e diretas, como "abra o navegador", devem ser a base do treinamento, e frases mais longas podem ser adicionadas posteriormente, após garantir a robustez do modelo para os comandos simples.

### 4. **Validação Contínua e Reestruturação dos Rótulos**

- Conforme os dados escalarem, será importante realizar **revisões periódicas** do dataset para garantir que os rótulos não estão se tornando redundantes ou desnecessariamente complicados.
- O uso de scripts automáticos para validar a consistência dos rótulos e a detecção de sobreposições entre rótulos ajudará a manter a estrutura clara e eficaz.

---

# Problemas Identificados no Modelo de Classificação

## Confusão do Modelo com Muitos Exemplos de Classificação

Um problema importante identificado é que o modelo começa a se confundir à medida que mais exemplos de classificação são adicionados. Embora o modelo tenha um bom desempenho com frases simples e comandos claros, ele enfrenta dificuldades ao lidar com uma maior diversidade de frases, especialmente quando comandos aparecem em diferentes posições ou quando existem múltiplas funções na frase.

### Comportamento do Modelo

1. **Comandos em Posições Variadas**:
   - O modelo foi treinado majoritariamente com comandos no início das frases. Quando comandos aparecem no meio ou no final, o modelo tem dificuldade em identificá-los corretamente, frequentemente rotulando palavras temporais ou sequenciais como comandos, o que resulta em erros.
   
2. **Confusão entre "Comando", "Função" e "Entidade"**:
   - Há uma clara confusão entre os rótulos de **Comando**, **Função** e **Entidade**. Em frases complexas, o modelo classifica verbos que deveriam ser comandos como "Função" ou "Entidade", confundindo as ações reais com descrições ou entidades.

3. **Palavras Temporais Classificadas Incorretamente**:
   - Palavras que indicam tempo, como "Antes", "Depois" e "Após", estão sendo incorretamente classificadas como "Comando", quando deveriam estar em um rótulo mais adequado, como "Tempo" ou "Outro". Isso afeta negativamente a precisão da classificação.

4. **Baixa Qualidade de Dados**:
   - Outro ponto importante é que o dataset usado no treinamento parece carecer de diversidade e exemplos robustos. Com um número limitado de exemplos que capturam diferentes estruturas de frases, o modelo acaba generalizando mal e cometendo erros em frases mais complexas.

### Principais Causas Identificadas

- **Desbalanceamento no Dataset**: O modelo foi treinado com uma quantidade maior de frases simples, onde os comandos estão no início da frase. Isso faz com que ele tenha dificuldades em lidar com comandos que aparecem em outras partes da frase.
  
- **Insuficiência de Exemplos de Funções e Entidades**: O modelo tem poucos exemplos que capturam corretamente a distinção entre funções, entidades e comandos, o que resulta em confusão entre esses rótulos em frases mais longas.

- **Problemas na Generalização**: À medida que mais dados são introduzidos, o modelo não consegue generalizar adequadamente, levando a uma maior taxa de erro quando é confrontado com frases que possuem múltiplas ações ou complexidades contextuais.

Esses problemas de classificação precisam ser corrigidos para que o modelo possa melhorar seu desempenho, especialmente ao lidar com frases complexas e comandos em posições não convencionais.


