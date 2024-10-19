# Axiom v0.01 (Alpha_phase 1/2)

Axiom é um projeto de inteligência artificial focado em treinar uma rede neural (RN) para a correta classificação de frases. Nesta fase, o objetivo é ajustar a RN para reconhecer e classificar corretamente os padrões de frases em várias categorias, como Comando, Entidade, Outro, Função, Tempo, Site, Navegador, Valor e Nenhum.

Esta versão está na fase **Alpha_phase 1/2**, o que significa que o projeto está em fase inicial, com foco em treinar e testar a rede neural, além de corrigir erros relacionados à classificação. O modelo pode variar significativamente sua precisão dependendo da quantidade e qualidade dos dados disponíveis para treinamento.

## Objetivo do Projeto

O objetivo principal do **Axiom v0.01** é classificar corretamente frases em diferentes categorias com base no conteúdo da frase. Essa fase do projeto está focada em resolver problemas como:

- **Ruídos nas Classificações**: Correções de erros onde palavras auxiliares são classificadas incorretamente (por exemplo, a palavra "o" sendo rotulada como parte da classe "Entidade").
- **Aprimoramento do Dataset Incremental**: Adição de mais dados limpos e exemplos variados para treinar o modelo, melhorando sua capacidade de generalização.
- **Ajuste de Precisão**: Melhorar o equilíbrio entre precisão, recall e F1-Score nas classes que estão apresentando baixo desempenho.

## Classes Utilizadas no Modelo

1. **Comando**: Identifica comandos específicos nas frases (e.g., "abra", "verifique").
2. **Entidade**: Classifica palavras ou expressões que representam entidades (e.g., "receitas", "correios").
3. **Outro**: Captura palavras auxiliares que não se enquadram nas outras classes (e.g., "o", "e", "no", "para").
4. **Função**: Classifica funções ou ações nas frases (e.g., "pesquise", "verifique").
5. **Tempo**: Identifica termos relacionados ao tempo (e.g., "amanhã").
6. **Site**: Classifica nomes de sites mencionados nas frases (e.g., "TudoGostoso", "Correios").
7. **Navegador**: Captura os navegadores mencionados (e.g., "Google Chrome", "Firefox").
8. **Valor**: Identifica valores numéricos e quantidades (e.g., "180 graus", "15%").
9. **Nenhum**: Para palavras ou expressões que não pertencem a nenhuma das categorias anteriores.

## Exemplo de Classificação

Aqui está um exemplo de entrada de uma frase e sua respectiva saída de classificação:

### Frase de Exemplo:

"Abra o navegador Google Chrome e pesquise por receitas no site TudoGostoso para preparar amanhã, ajustando a temperatura do forno para 180 graus e verificando o status da entrega no site dos Correios."

### Classificação Esperada (Rótulos):

```json
[
    {
    "Frase": "Abra o navegador Google Chrome e pesquise por receitas no site TudoGostoso para preparar amanhã, ajustando a temperatura do forno para 180 graus e verificando o status da entrega no site dos Correios.",
    "Rótulos": {
        "Comando": ["abra", "pesquise"],
        "Outro": ["o", "e", "por", "no", "para", "a", "do", "para", "e", "o", "da", "no", "dos"],
        "Função": ["ajustando", "verificando"],
        "Entidade": ["receitas", "temperatura", "forno", "entrega"],
        "Valor": ["180 graus"],
        "Tempo": ["amanhã"],
        "Site": ["TudoGostoso", "Correios"],
        "Navegador": ["Google Chrome"]
        }
    }
]
```

## Resultados de Métricas e Acurácia Atual

### Principais Métricas:
- **Acurácia Global**: 64%
- **Macro Average**:
  - Precisão: 0.53
  - Recall: 0.56
  - F1-Score: 0.49
- **Weighted Average**:
  - Precisão: 0.65
  - Recall: 0.64
  - F1-Score: 0.61

### Desempenho por Classe:

| Classe     | Precisão | Recall | F1-Score | Suporte |
|------------|----------|--------|----------|---------|
| Comando    | 1.00     | 0.25   | 0.40     | 4       |
| Entidade   | 0.80     | 0.80   | 0.80     | 5       |
| Outro      | 0.85     | 1.00   | 0.92     | 11      |
| Função     | 0.17     | 1.00   | 0.29     | 1       |
| Tempo      | 1.00     | 1.00   | 1.00     | 1       |
| Site       | 0.00     | 0.00   | 0.00     | 2       |
| Navegador  | 1.00     | 1.00   | 1.00     | 3       |
| Valor      | 0.00     | 0.00   | 0.00     | 2       |
| Nenhum     | 0.00     | 0.00   | 0.00     | 4       |

### Observações:
- **Desempenho de "Comando"**: Apesar de uma precisão alta, o recall é baixo, indicando que o modelo não está capturando todos os comandos esperados.
- **Entidade e Outro**: Apresentam bom desempenho, com equilíbrio entre precisão e recall.
- **Função e Site**: Ainda requerem mais ajustes devido ao baixo desempenho.
- **Classe "Valor"**: Precisa de mais exemplos no dataset para melhorar a precisão e recall.

---

## Como Usar

Adicione as frases que você deseja classificar no arquivo **classificacoes.json**. O modelo processará essas frases e gerará uma saída contendo as classificações para cada palavra.

### Exemplo de entrada de frase no arquivo **classificacoes.json**:

```json
{
    "Frase": "Abra o navegador e pesquise por notícias no Google.",
    "Rótulos": {
        "Comando": ["abra", "pesquise"],
        "Outro": ["o", "e", "por", "no"],
        "Função": [],
        "Entidade": ["notícias"],
        "Site": ["google"],
        "Navegador": ["navegador"]
    }
}
```

----------------------------------------------------

Status do Projeto
Versão Atual: Axiom v0.01 (Alpha_phase 1/2)
Esta versão está na fase inicial do projeto, e o foco é melhorar o treinamento do modelo e corrigir erros nas classificações de frases. O sistema ainda não está pronto para produção, e os resultados podem variar entre 30% a 100% de acurácia, dependendo da classe avaliada e da quantidade de dados disponíveis para treinamento.
