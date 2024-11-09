import re
import json
import torch
from transformers import RobertaTokenizerFast, RobertaForTokenClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

# Verificar se CUDA está disponível
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Dicionário de mapeamento dinâmico para os rótulos
rotulo_map = {
    "Comando": 0,
    "Entidade": 1,
    "Outro": 2,
    "Funcao": 3,
    "Tempo": 4,
    "Site": 5,    
    "Navegador": 6,
    "Valor": 7,
    "Qualidade": 8,
    "Estado": 9,
    "Nome": 10
}

# Função para identificar valores monetários e percentuais
def tratar_valores(frase):
    frase = re.sub(r'(\bR\$|\bUS\$|\€)(\d+)', r'\1\2', frase)  # Exemplo: "R$150"
    frase = re.sub(r'(\d+)(%)', r'\1\2', frase)  # Exemplo: "50%"
    return frase

# Função para processar o JSON com rótulos dinâmicos (multi-label)
def carregar_dataset_json(caminho_json):
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_json} não foi encontrado.")
        exit()
    except json.JSONDecodeError:
        print(f"Erro: O arquivo {caminho_json} não é um JSON válido.")
        exit()

    frases_split = []
    labels = []
    for item in data:
        frase = tratar_valores(item['Frase'])
        frase = frase.split()
        rotulos = item['Rótulos']

        frase_labels = []
        for palavra in frase:
            multi_label = [0] * len(rotulo_map)  # Vetor para multi-rótulo
            for rotulo, valor in rotulos.items():
                if valor is None:
                    continue
                if isinstance(valor, str) and palavra.lower() in valor.lower():
                    if rotulo in rotulo_map:
                        multi_label[rotulo_map[rotulo]] = 1
                elif isinstance(valor, list) and palavra.lower() in [w.lower() for w in valor]:
                    if rotulo in rotulo_map:
                        multi_label[rotulo_map[rotulo]] = 1
            frase_labels.append(multi_label if any(multi_label) else [-100] * len(rotulo_map))

        frases_split.append(frase)
        labels.append(frase_labels)

    return frases_split, labels

# Classe do Dataset customizado
class TokenClassificationDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.float)
        return item

    def __len__(self):
        return len(self.labels)

# Função para alinhar os labels com os tokens
def align_labels_with_tokens(labels, encodings):
    aligned_labels = []
    for i in range(len(encodings['input_ids'])):
        word_ids = encodings.word_ids(batch_index=i)
        label = labels[i]
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append([-100]*len(rotulo_map))
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append([-100]*len(rotulo_map))
            previous_word_idx = word_idx
        aligned_labels.append(label_ids)
    return aligned_labels

# Caminho do arquivo de dados de treinamento
caminho_treino = 'dataset_incremental.json'

# Carregar os dados de treinamento
frases_split, labels = carregar_dataset_json(caminho_treino)

# Verificar se o dataset foi carregado corretamente
if not frases_split or not labels:
    print("Erro: O dataset não foi carregado corretamente ou está vazio.")
    exit()

# Dividir os dados em treinamento e teste
try:
    train_frases_split, test_frases_split, train_labels, test_labels = train_test_split(
        frases_split, labels, test_size=0.2, random_state=42
    )
except ValueError as e:
    print(f"Erro ao dividir os dados: {e}")
    exit()

# Inicializar o tokenizer
try:
    tokenizer = RobertaTokenizerFast.from_pretrained('roberta-large', add_prefix_space=True)
except Exception as e:
    print(f"Erro ao carregar o tokenizer: {e}")
    exit()

# Preparar os dados de treinamento e teste
try:
    train_encodings = tokenizer(train_frases_split, is_split_into_words=True, return_offsets_mapping=True, padding=True, truncation=True)
    train_labels_aligned = align_labels_with_tokens(train_labels, train_encodings)
    train_encodings.pop("offset_mapping")
    train_dataset = TokenClassificationDataset(train_encodings, train_labels_aligned)

    test_encodings = tokenizer(test_frases_split, is_split_into_words=True, return_offsets_mapping=True, padding=True, truncation=True)
    test_labels_aligned = align_labels_with_tokens(test_labels, test_encodings)
    test_encodings.pop("offset_mapping")
    test_dataset = TokenClassificationDataset(test_encodings, test_labels_aligned)
except Exception as e:
    print(f"Erro ao preparar os dados: {e}")
    exit()

# Carregar o modelo salvo
try:
    model_path = 'results'
    model = RobertaForTokenClassification.from_pretrained(model_path)
    model.to(device)
except FileNotFoundError:
    print(f"Erro: O modelo salvo em {model_path} não foi encontrado.")
    exit()
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    exit()

# Função para converter previsões em rótulos binários
def obter_predicoes(model, dataset):
    model.eval()
    all_preds = []
    all_labels = []

    for i in range(len(dataset)):
        batch = dataset[i]
        inputs = {key: val.unsqueeze(0).to(device) for key, val in batch.items() if key != 'labels'}
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        # Converta logits em previsões binárias
        preds = torch.sigmoid(logits).cpu().numpy()
        preds = (preds > 0.5).astype(int)  # Limite de 0.5 para binário

        # Coletar os rótulos e aplicar a máscara para tokens válidos (não -100)
        labels = batch['labels'].cpu().numpy()
        mask = np.any(labels != -100, axis=1)

        valid_preds = preds.reshape(-1, preds.shape[-1])[mask]
        valid_labels = labels.reshape(-1, labels.shape[-1])[mask]

        all_preds.extend(valid_preds)
        all_labels.extend(valid_labels)

    return np.array(all_preds), np.array(all_labels)

# Obter previsões e rótulos do conjunto de teste
try:
    predicoes, rótulos_reais = obter_predicoes(model, test_dataset)
except Exception as e:
    print(f"Erro durante a inferência: {e}")
    exit()

# Verificar se o tamanho das previsões e dos rótulos está correto
if len(predicoes) != len(rótulos_reais):
    print("Erro: As previsões e os rótulos reais não têm o mesmo comprimento após a filtragem.")
    exit()

# Calcular métricas de desempenho
try:
    report = classification_report(rótulos_reais, predicoes, target_names=list(rotulo_map.keys()), zero_division=0)
    print(report)
except Exception as e:
    print(f"Erro ao calcular o relatório de classificação: {e}")
    exit()
