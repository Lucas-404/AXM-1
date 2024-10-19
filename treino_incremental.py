import re
import json
import torch
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments
import os

# Dicionário de rótulos (mesmo do treino geral)
rotulo_map = {
    "Comando": 0,
    "Entidade": 1,
    "Outro": 2,
    "Funcao": 3,
    "Tempo": 4,
    "Site": 5,    
    "Navegador": 6,
    "Valor": 7
}

# Função para identificar valores monetários e percentuais
def tratar_valores(frase):
    frase = re.sub(r'(\bR\$|\bUS\$|\€)(\d+)', r'\1\2', frase)  # Exemplo: "R$150"
    frase = re.sub(r'(\d+)(%)', r'\1\2', frase)  # Exemplo: "50%"
    return frase

# Função para processar o JSON com rótulos dinâmicos (multi-label)
def carregar_dataset_json(caminho_json):
    with open(caminho_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    frases_split = []
    labels = []
    for item in data:
        frase = tratar_valores(item['Frase'])  # Tratar valores monetários e percentuais
        frase = frase.split()  # Quebrar a frase em palavras
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
            # Se não houver rótulo para a palavra, adicionar -100 (ignorar)
            frase_labels.append(multi_label if any(multi_label) else [-100] * len(rotulo_map))

        frases_split.append(frase)
        labels.append(frase_labels)

    return frases_split, labels

# Caminho do arquivo JSON com os novos dados
caminho_json_novos_dados = 'E:\\Classificao\\dataset_incremental.json'

# Carregar o modelo previamente salvo
output_dir = os.path.join(os.getcwd(), 'results')  # Diretório onde o modelo anterior foi salvo
model = BertForTokenClassification.from_pretrained(output_dir, num_labels=len(rotulo_map))  # Carrega o modelo salvo
tokenizer = BertTokenizerFast.from_pretrained(output_dir)  # Carrega o tokenizer salvo

# Carregar e processar os novos dados
frases_split_novos, labels_novos = carregar_dataset_json(caminho_json_novos_dados)
encodings_novos = tokenizer(frases_split_novos, is_split_into_words=True, return_offsets_mapping=True, padding=True, truncation=True)

# Remover o mapeamento de offsets, pois não é mais necessário
encodings_novos.pop("offset_mapping")

# Alinhar os rótulos com os tokens
aligned_labels_novos = []
for i in range(len(frases_split_novos)):
    word_ids = encodings_novos.word_ids(batch_index=i)
    label = labels_novos[i]
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
    aligned_labels_novos.append(label_ids)

# Dataset customizado para os novos dados
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

# Criar o dataset com os novos dados
novo_dataset = TokenClassificationDataset(encodings_novos, aligned_labels_novos)

# Configurações de treinamento incremental
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=8,  # Tamanho do batch
    num_train_epochs=10,  # Número de épocas para o treino incremental
    logging_dir='./logs',
    logging_steps=1,
    save_steps=1,
    save_total_limit=2,  # Limite de checkpoints salvos
    report_to="none"  # Desabilitar relatórios (WandB, TensorBoard)
)

# Subclasse do Trainer para o treinamento incremental
class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")  # Retirar os rótulos da entrada
        outputs = model(**inputs)
        logits = outputs.get("logits")

        # Alinhar os logits e os rótulos
        logits = logits.view(-1, model.num_labels)
        labels = labels.view(-1, model.num_labels)

        active_loss = labels.sum(dim=1) != (-100) * model.num_labels  # Ignorar os rótulos -100
        active_logits = logits[active_loss]
        active_labels = labels[active_loss]

        loss_fct = torch.nn.BCEWithLogitsLoss()  # Função de perda para multi-label
        loss = loss_fct(active_logits, active_labels)
        return (loss, outputs) if return_outputs else loss

# Definir o trainer para o treinamento incremental
trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=novo_dataset,
)

# Continuar o treinamento com os novos dados
trainer.train()

# Salvar o modelo novamente após o treinamento incremental
trainer.save_model(output_dir)  # Salvar o modelo atualizado
trainer.state.save_to_json(os.path.join(output_dir, "trainer_state_incremental.json"))  # Salvar o estado
tokenizer.save_pretrained(output_dir)  # Salvar o tokenizer

# Teste de escrita em arquivo após o treino incremental
with open(os.path.join(output_dir, "test_incremental.txt"), "a") as f:
    f.write("Treinamento incremental concluído com sucesso.")
