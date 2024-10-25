# Changelog

## [v0.01 (Alpha_phase 1/2)] - 18-10-2024
- Implementação inicial da rede neural para classificação de frases.
- Foco na correção de ruídos nas classificações, como o tratamento de palavras auxiliares incorretas.
- Primeira fase de testes: avaliação de precisão e melhorias nas classes "Comando", "Entidade", "Outro".
- Limitações: Classes como "Valor" e "Site" estão em fase de refinamento, precisando de mais exemplos no dataset incremental.

## [v0.01 (Alpha_phase 1/2)] - 25/10/2024
### Added
- Troca de arquitetura de BERT para RoBERTa-large
- Ajuste no código de treinamento para lidar com mais classes dinâmicas
- Adição de novos datasets reformulados.

### Fixed
- Problemas de instabilidade ao lidar com classes ambíguas, como "Comando" e "Função"
