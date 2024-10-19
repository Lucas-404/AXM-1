#AXM-1

Projeto de Classificação de Frases
Este projeto visa criar um modelo de classificação de frases utilizando aprendizado de máquina, com base em classes como Comando, Entidade, Outro, Função, Tempo, Site, Navegador, Valor, e Nenhum. O objetivo é avaliar a precisão e melhorar o desempenho de cada classe com base em um dataset incremental.

Descrição do Projeto
O projeto envolve um modelo de classificação que recebe frases e as categoriza em diferentes classes de acordo com o conteúdo da frase. Com a utilização de aprendizado supervisionado, o modelo é treinado com exemplos de frases rotuladas e gera previsões para novas frases. Cada frase é analisada e classificada em várias categorias.

Classes Utilizadas no Modelo
Comando: Identifica comandos específicos nas frases (e.g., "abra", "verifique").
Entidade: Classifica palavras ou expressões que representam entidades (e.g., "receitas", "correios").
Outro: Captura palavras auxiliares que não se enquadram nas outras classes (e.g., "e", "no", "para").
Função: Classifica funções ou ações nas frases (e.g., "pesquise", "verifique").
Tempo: Identifica termos relacionados ao tempo (e.g., "amanhã").
Site: Classifica nomes de sites mencionados nas frases (e.g., "TudoGostoso", "Correios").
Navegador: Captura os navegadores mencionados nas frases (e.g., "Google Chrome", "Firefox").
Valor: Identifica valores numéricos e quantidades (e.g., "180 graus", "15%").
Nenhum: Para palavras ou expressões que não pertencem a nenhuma das categorias anteriores.

Adicione as frases que deseja classificar no arquivo classificacoes.json. Exemplo de entrada de frase:

json
Copiar código
{
    "Frase": "Abra o navegador e pesquise por notícias no Google.",
    "Rótulos": {
        "Comando": ["abra", "pesquise"],
        "Outro": ["o", "e", "por", "no"],
        "Funcao": ["pesquise"],
        "Entidade": ["notícias"],
        "Site": ["google"],
        "Navegador": ["navegador"]
    }
}
O modelo irá gerar uma saída no terminal com as métricas de desempenho, como precisão, recall e F1-Score para cada classe identificada.

Exemplo de Saída
Aqui está um exemplo de métrica de saída para uma frase processada:

markdown
Copiar código
              precision    recall  f1-score   support
     Comando       1.00      0.85      0.92        71
    Entidade       0.74      0.85      0.79       113
       Outro       0.95      0.97      0.96       214
      Funcao       0.78      0.85      0.82        62
       Tempo       0.45      0.31      0.37        16
        Site       0.58      0.48      0.52        23
   Navegador       0.33      0.50      0.40         4
       Valor       0.80      0.80      0.80        10
      Nenhum       0.00      0.00      0.00        16

    accuracy                           0.84       529
   macro avg       0.63      0.62      0.62       529
weighted avg       0.82      0.84      0.83       529
Contribuição
Contribuições são sempre bem-vindas! Se você encontrar algum bug ou tiver sugestões de melhorias, sinta-se à vontade para abrir um issue ou fazer um pull request.

Licença
Este projeto está sob a licença MIT - veja o arquivo LICENSE para mais detalhes.
