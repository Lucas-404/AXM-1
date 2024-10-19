from transformers import BertTokenizerFast, BertForTokenClassification
import torch
import re
import json

# Caminhos para o modelo e tokenizer salvos
model_path = './results'  # O caminho onde você salvou o modelo

# Carregar o tokenizer
tokenizer = BertTokenizerFast.from_pretrained(model_path)

# Carregar o modelo usando 'weights_only=True' para evitar o aviso
state_dict = torch.load(f"{model_path}/pytorch_model.bin", map_location="cpu", weights_only=True)
model = BertForTokenClassification.from_pretrained(model_path, state_dict=state_dict)

# Função auxiliar para verificar se um token é um token de valor
def is_value_token(token):
    # Símbolos de valor e tokens de moeda conhecidos
    value_symbols = {"$", "€", "£", "%"}
    currency_tokens = {"R$", "US$", "US", "R", "U$", "€", "£"}
    # Remover prefixo '##' se existir
    token_clean = token.lstrip("##")
    # Verificar se o token é um símbolo de valor ou contém dígitos
    if token_clean in value_symbols or token_clean in currency_tokens:
        return True
    if token_clean.isdigit():
        return True
    if re.search(r'\d', token_clean):
        return True
    return False

# Função para realizar a inferência em uma frase
def classify_sentence(sentence):
    try:
        # Tokenizar a frase
        inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
        
        # Colocar o modelo em modo de avaliação
        model.eval()
        
        # Fazer a inferência
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Obter as previsões e converter para rótulos
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)
        
        # Decodificar tokens e labels
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        labels = predictions[0].tolist()
        
        # Mapeamento de rótulos
        label_map = {
            0: "Comando", 1: "Entidade", 2: "Outro", 3: "Funcao",
            4: "Tempo", 5: "Site", 6: "Navegador", 7: "Valor"
        }
        
        # Inicializando o dicionário para as classificações
        final_output = {
            "Frase": sentence,
            "Rótulos": {
                "Comando": [],
                "Outro": [],
                "Funcao": [],
                "Entidade": [],
                "Valor": [],
                "Tempo": [],
                "Site": [],
                "Navegador": []
            }
        }
        
        # Definir stopwords e palavras de entidade
        stopwords = {"e", "ou", "mas", "porém", "todavia", "contudo", "entretanto"}
        entity_words = {"produto", "produtos", "oportunidade", "oportunidades", "serviço", "serviços"}
        
        # Função para verificar se o token é pontuação
        import string

        def is_punctuation(token):
            # Excluir '$' e '%' dos caracteres de pontuação
            punctuation_chars = set(string.punctuation) - set('$%')
            return all(char in punctuation_chars for char in token)
        
        # Inicialização das variáveis
        current_word = ""
        current_label = None
        in_value_sequence = False
        
        for token, label in zip(tokens, labels):
            if token in ["[CLS]", "[SEP]"]:
                continue
            
            # Ignorar tokens de pontuação (excluindo '$' e '%')
            if is_punctuation(token):
                continue

            token_clean = token.lstrip("##")
            label_name = label_map.get(label, "Desconhecido")
            
            # Override do rótulo se o token for uma stopword
            if token_clean.lower() in stopwords:
                label_name = "Outro"
            # Override do rótulo se o token for uma entidade conhecida
            elif token_clean.lower() in entity_words:
                label_name = "Entidade"
            
            # Verificar se o token é parte de um valor
            if label_name == "Valor" or is_value_token(token):
                if in_value_sequence:
                    # Continuar a sequência de valor
                    current_word += token_clean
                else:
                    # Salvar a palavra anterior
                    if current_word and current_label:
                        # Verificar se a palavra é uma entidade conhecida
                        if current_word.lower() in entity_words:
                            current_label = "Entidade"
                        final_output["Rótulos"].setdefault(current_label, []).append(current_word)
                    # Iniciar uma nova sequência de valor
                    current_word = token_clean
                    current_label = "Valor"
                    in_value_sequence = True
            else:
                # Se estávamos em uma sequência de valor, finalizá-la
                if in_value_sequence:
                    final_output["Rótulos"].setdefault(current_label, []).append(current_word)
                    current_word = ""
                    in_value_sequence = False
                
                # Reconstrução de palavras a partir de subtokens
                if token.startswith("##"):
                    current_word += token_clean
                else:
                    # Salvar a palavra anterior
                    if current_word and current_label:
                        # Verificar se a palavra é uma entidade conhecida
                        if current_word.lower() in entity_words:
                            current_label = "Entidade"
                        final_output["Rótulos"].setdefault(current_label, []).append(current_word)
                    # Iniciar uma nova palavra
                    current_word = token_clean
                    current_label = label_name
        
        # Adicionar a última palavra após o loop
        if current_word and current_label:
            # Verificar se a palavra é uma entidade conhecida
            if current_word.lower() in entity_words:
                current_label = "Entidade"
            final_output["Rótulos"].setdefault(current_label, []).append(current_word)
    
        return final_output

    except Exception as e:
        print(f"Erro durante a inferência: {e}")
        return None

# Função para processar múltiplas frases e salvar em JSON
def process_and_save(sentences, output_json_path):
    results = []
    for sentence in sentences:
        classification = classify_sentence(sentence)
        if classification:
            results.append(classification)
    
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

# Exemplo de frases
test_sentences = [
   "Abra o navegador Google Chrome e pesquise por receitas no site TudoGostoso para preparar amanhã, ajustando a temperatura do forno para 180 graus e verificando o status da entrega no site dos Correios."
]

# Caminho para salvar o arquivo JSON
output_json_file = "classificacoes.json"

# Processar as frases e salvar o resultado no arquivo JSON
process_and_save(test_sentences, output_json_file)

print(f"Resultados salvos em {output_json_file}")
