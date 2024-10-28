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

Um dos problemas principais identificados no modelo é a sua incapacidade de lidar com uma grande quantidade de dados durante a inferência. Quando o modelo recebe muitas frases ou exemplos de classificação de uma só vez, ele apresenta dificuldades em classificar corretamente. No entanto, quando apenas uma frase é processada de cada vez, o modelo consegue realizar a classificação de forma correta e precisa.

### Comportamento do Modelo

1. **Desempenho Corretamente com Uma Frase**:
   - Quando o modelo é alimentado com apenas uma frase para inferência, ele geralmente consegue classificar corretamente, identificando comandos, funções e entidades de maneira precisa. Isso indica que o modelo é capaz de realizar a tarefa com sucesso quando a quantidade de dados é limitada.

2. **Desempenho Degrada com Muitas Frases**:
   - Ao processar uma grande quantidade de frases, o modelo se confunde e a taxa de erros aumenta significativamente. Ele começa a fazer classificações incorretas, como identificar palavras temporais como comandos ou confundir funções com entidades. Isso sugere uma limitação no processamento em massa, que impacta diretamente a precisão da inferência.

3. **Erros em Frases Complexas**:
   - O modelo também parece ter dificuldades ao lidar com frases mais complexas quando são processadas em grande volume. Em frases onde existem múltiplas ações ou comandos em posições não convencionais (no meio ou no final da frase), o modelo apresenta um aumento no número de erros.

### Principais Causas Identificadas

- **Sobrecarga de Inferência**: O modelo parece não estar otimizado para lidar com muitos dados ao mesmo tempo, levando a uma degradação de desempenho quando processa várias frases em paralelo.

- **Falta de Generalização**: A capacidade do modelo de generalizar corretamente parece limitada quando confrontado com uma grande quantidade de exemplos, resultando em confusões frequentes entre diferentes rótulos.

- **Quantidade de Dados no Treinamento**: A quantidade e a qualidade dos dados usados no treinamento podem não ter sido suficientes para preparar o modelo para cenários em que há uma grande diversidade de frases, especialmente quando são introduzidas muitas frases ao mesmo tempo.

O comportamento inconsistente do modelo com grandes volumes de dados deve ser investigado mais a fundo para identificar a origem do problema e melhorar sua capacidade de lidar com inferências em massa.



