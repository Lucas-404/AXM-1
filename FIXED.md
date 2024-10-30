### **Fixed**

- **Ambiguidade e Classificação Incorreta**: 
  - Corrigimos a ambiguidade entre rótulos, especialmente em palavras temporais como "Após" e "Antes", que eram classificadas como "Comando", e agora são corretamente categorizadas como "Tempo".
  - Ajustamos a classificação de adjetivos como "corretamente" e "necessário", que estavam sendo rotulados incorretamente como "Função" ou "Tempo" e agora são classificados como "Outro" ou "Função", conforme o contexto.

- **Frases Longas com Poucos Rótulos**: 
  - Implementamos melhorias para lidar com frases mais longas e complexas, garantindo uma melhor precisão mesmo com um número limitado de rótulos. Isso reduziu as ambiguidades que surgiam em frases maiores.

- **Escalabilidade em Frases Longas**:
  - Fizemos ajustes na escalabilidade para melhorar a classificação de frases longas e complexas sem gerar um número excessivo de rótulos. O modelo agora consegue lidar melhor com frases que contêm várias entidades e ações.
