## Changelog

Este changelog documenta as principais mudanças no projeto de criação de um modelo para classificação de frases com RoBERTa-large. O foco principal é melhorar a precisão em classes ambíguas e expandir a capacidade do modelo para lidar com novos rótulos. A seguir, estão listadas as mudanças, adições e correções em cada versão do projeto.

### v0.01 (Alpha_phase 1/2) - 18-10-2024
#### Added
- Implementação inicial da rede neural para classificação de frases.
- Foco na correção de ruídos nas classificações, como o tratamento de palavras auxiliares incorretas.
- Primeira fase de testes: avaliação de precisão e melhorias nas classes "Comando", "Entidade", "Outro".
  
#### Known Issues
- Limitações: Classes como "Valor" e "Site" estão em fase de refinamento, precisando de mais exemplos no dataset incremental.

---

### v0.01 (Alpha_phase 1/2) - 25-10-2024
#### Added
- **Troca de arquitetura**: Mudança de BERT para RoBERTa-large, resultando em melhor estabilidade e desempenho em classificações mais complexas.
- **Ajuste no código de treinamento**: Suporte adicionado para lidar com mais classes dinâmicas, permitindo maior flexibilidade do modelo em relação a novos rótulos.
- **Adição de novos datasets reformulados**: Novos exemplos de dataset foram adicionados para melhorar a precisão e cobrir mais casos específicos.

#### Fixed
- **Problemas de instabilidade**: Correção de erros ao lidar com classes ambíguas, como "Comando" e "Função", melhorando a precisão em frases com comandos que também podem ser interpretados como funções.

#### Known Issues
- **Ambiguidades remanescentes**: Ainda existem casos ambíguos entre "Comando" e "Função" que podem necessitar de refinamentos adicionais no dataset.
- **Classes "Valor" e "Site"**: Precisam de mais exemplos no dataset incremental para melhorar a performance.

---

## v0.01 (Alpha Phase 1/2) - 27-10-2024

### **Added**
- Mais rótulos foram adicionados ao dataset para melhorar a precisão em frases maiores e mais complexas, permitindo ao modelo lidar com mais variações.
- Implementação de categorias dinâmicas de rótulos para classificar palavras com maior flexibilidade, conforme a natureza das frases mais longas.
- Expansão do dataset com exemplos mais diversos para cobrir casos específicos de comandos mistos e frases descritivas.

### **Fixed**
- Correção de inconsistências no treinamento em frases curtas, com melhorias na classificação de palavras em rótulos como "Comando" e "Entidade".
- Ajustes na segmentação de frases para melhorar a correspondência entre palavras e seus rótulos em frases longas, garantindo uma melhor precisão nas previsões.

### **Known Issues**
- **Falta de rótulos suficientes para frases complexas**: O modelo enfrenta dificuldades ao classificar frases mais longas, especialmente quando comandos, entidades e referências temporais coexistem. Novos rótulos estão sendo considerados para resolver essa questão.
- **Ambiguidade entre categorias**: Algumas palavras são classificadas de forma ambígua entre rótulos como "Comando", "Função" e "Outro". Isso ocorre especialmente em frases onde o comando pode ser interpretado de diferentes formas.
- **Problemas de escalabilidade com mais rótulos**: Com a adição de novos rótulos, a escalabilidade do dataset se tornou um problema. Frases longas geram muitas classificações, tornando o processo de rotulação e treinamento mais complexo.
