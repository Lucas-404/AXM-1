import re
import json
import torch
from transformers import RobertaTokenizerFast, RobertaForTokenClassification, Trainer, TrainingArguments, DataCollatorForTokenClassification
import os
from sklearn.model_selection import train_test_split  # Correção na importação

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
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        raise
    
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

# Caminho do arquivo JSON
caminho_json = 'dataset_treino.json'

# Carregar as frases e rótulos do JSON
frases_split, labels = carregar_dataset_json(caminho_json)

# Verificar se os rótulos correspondem ao número de palavras
for i in range(len(frases_split)):
    if len(labels[i]) != len(frases_split[i]):
        print(f"Atenção: A frase '{' '.join(frases_split[i])}' tem {len(frases_split[i])} palavras, mas {len(labels[i])} rótulos.")

# Carregar o tokenizer com add_prefix_space=True para entradas pré-tokenizadas
tokenizer = RobertaTokenizerFast.from_pretrained('roberta-large', add_prefix_space=True)
model = RobertaForTokenClassification.from_pretrained('roberta-large', num_labels=len(rotulo_map))
model.to(device)

# Tokenizar as frases
encodings = tokenizer(frases_split, is_split_into_words=True, return_offsets_mapping=True, padding=True, truncation=True)

# Remover o mapeamento de offsets, pois não é mais necessário
encodings.pop("offset_mapping")

# Alinhar os rótulos com os tokens
aligned_labels = []
for i in range(len(frases_split)):
    word_ids = encodings.word_ids(batch_index=i)
    label = labels[i]
    label_ids = []
    previous_word_idx = None
    for word_idx in word_ids:
        if word_idx is None:
            label_ids.append([-100] * len(rotulo_map))  # Ignorar tokens especiais
        elif word_idx != previous_word_idx:  # Primeiro token da palavra
            label_ids.append([float(l) for l in label[word_idx]])  # Aplicar os múltiplos rótulos
        else:
            label_ids.append([-100] * len(rotulo_map))  # Ignorar sub-palavras
        previous_word_idx = word_idx
    aligned_labels.append(label_ids)

# Atualizar os encodings com os labels alinhados
encodings['labels'] = aligned_labels

# Definir o Dataset customizado para o treinamento
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

# Criar o dataset usando a classe customizada
dataset = TokenClassificationDataset(encodings, aligned_labels)

# Dividir o dataset em treinamento e validação usando sklearn
train_indices, val_indices = train_test_split(range(len(dataset)), test_size=0.2, random_state=42)
train_dataset = torch.utils.data.Subset(dataset, train_indices)
val_dataset = torch.utils.data.Subset(dataset, val_indices)

# Utilizar Data Collator para lidar com padding
data_collator = DataCollatorForTokenClassification(tokenizer)

# Subclasse do Trainer para sobrescrever compute_loss
class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        logits = logits.view(-1, model.num_labels)
        labels = labels.view(-1, model.num_labels).float()  # Converte as labels para float

        active_loss = labels.sum(dim=1) != (-100) * model.num_labels
        active_logits = logits[active_loss]
        active_labels = labels[active_loss]

        loss_fct = torch.nn.BCEWithLogitsLoss()
        loss = loss_fct(active_logits, active_labels)
        return (loss, outputs) if return_outputs else loss

# Caminho absoluto para salvar os resultados
output_dir = os.path.join(os.getcwd(), 'results')

# Configurações de treinamento aprimoradas
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=16,  # Ajustado para roberta-large
    num_train_epochs=10,
    evaluation_strategy='epoch',  # Adicionada avaliação em cada época
    logging_dir='./logs',
    logging_steps=10,
    save_steps=500,
    save_total_limit=2,
    report_to="none"
)

# Definir o trainer customizado
trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
)

# Treinamento do modelo
trainer.train()

# Salvar o modelo e o estado
trainer.save_model(output_dir)
trainer.state.save_to_json(os.path.join(output_dir, "trainer_state.json"))
tokenizer.save_pretrained(output_dir)

# Teste de criação de arquivo no diretório
with open(os.path.join(output_dir, "test.txt"), "a") as f:
    f.write("Teste de escrita bem-sucedido.")
