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

### v0.02 (Alpha_phase 1/2) - 25-10-2024
#### Added
- **Troca de arquitetura**: Mudança de BERT para RoBERTa-large, resultando em melhor estabilidade e desempenho em classificações mais complexas.
- **Ajuste no código de treinamento**: Suporte adicionado para lidar com mais classes dinâmicas, permitindo maior flexibilidade do modelo em relação a novos rótulos.
- **Adição de novos datasets reformulados**: Novos exemplos de dataset foram adicionados para melhorar a precisão e cobrir mais casos específicos.

#### Fixed
- **Problemas de instabilidade**: Correção de erros ao lidar com classes ambíguas, como "Comando" e "Função", melhorando a precisão em frases com comandos que também podem ser interpretados como funções.

#### Known Issues
- **Ambiguidades remanescentes**: Ainda existem casos ambíguos entre "Comando" e "Função" que podem necessitar de refinamentos adicionais no dataset.
- **Classes "Valor" e "Site"**: Precisam de mais exemplos no dataset incremental para melhorar a performance.


