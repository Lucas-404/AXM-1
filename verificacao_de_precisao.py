import json
from sklearn.metrics import classification_report
import unicodedata
import string
from difflib import SequenceMatcher

# Caminhos dos arquivos
caminho_dataset_incremental = 'E:\\Classificao\\dataset_incremental.json'
caminho_classificacoes = 'E:\\Classificao\\classificacoes.json'

# Mapeamento dos rótulos
rotulo_map = {
    "Comando": 0,
    "Entidade": 1,
    "Outro": 2,
    "Funcao": 3,
    "Tempo": 4,
    "Site": 5,
    "Navegador": 6,
    "Valor": 7,
    "Nenhum": 8
}

# Funções de normalização
def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def normalizar_frase(frase):
    frase = frase.lower().strip()
    frase = remover_acentos(frase)
    frase = frase.translate(str.maketrans('', '', string.punctuation))
    return frase

# Carregar os dados
with open(caminho_dataset_incremental, 'r', encoding='utf-8') as f:
    dataset_incremental = json.load(f)

with open(caminho_classificacoes, 'r', encoding='utf-8') as f:
    classificacoes = json.load(f)

# Criar mapeamento de frases normalizadas para itens
def criar_mapeamento(data):
    if isinstance(data, dict):  # Para aceitar apenas uma frase
        data = [data]
    mapping = {}
    for item in data:
        frase_norm = normalizar_frase(item['Frase'])
        mapping[frase_norm] = item
    return mapping

dataset_mapping = criar_mapeamento(dataset_incremental)

# Função para encontrar a melhor correspondência de frase
def encontrar_melhor_correspondencia(frase_norm, mapping, threshold=0.8):
    melhor_correspondencia = None
    maior_similaridade = 0
    for frase_dataset_norm in mapping.keys():
        similaridade = SequenceMatcher(None, frase_norm, frase_dataset_norm).ratio()
        if similaridade > maior_similaridade:
            maior_similaridade = similaridade
            melhor_correspondencia = frase_dataset_norm
    if maior_similaridade >= threshold:
        return melhor_correspondencia
    else:
        return None

# Função para atribuir rótulos considerando expressões de múltiplas palavras
def atribuir_rotulos(frase, rótulos_item):
    frase_normalizada = normalizar_frase(frase)
    tokens_frase = frase_normalizada.split()
    labels = [rotulo_map["Nenhum"]] * len(tokens_frase)

    for classe, palavras_classe in rótulos_item['Rótulos'].items():
        if palavras_classe:
            if isinstance(palavras_classe, str):
                palavras_classe = [palavras_classe]
            for expressao in palavras_classe:
                expressao_normalizada = normalizar_frase(expressao)
                tokens_expressao = expressao_normalizada.split()

                # Procurar a expressão na frase
                for i in range(len(tokens_frase) - len(tokens_expressao) + 1):
                    if tokens_frase[i:i+len(tokens_expressao)] == tokens_expressao:
                        for idx in range(i, i+len(tokens_expressao)):
                            labels[idx] = rotulo_map[classe]
    return labels

# Extrair rótulos e predições
rotulos_reais = []
rotulos_preditos = []
frases_palavras = []

# Se classificacoes for um dict, transformá-lo em uma lista com um único item
if isinstance(classificacoes, dict):
    classificacoes = [classificacoes]

for item_classif in classificacoes:
    frase_classif = item_classif['Frase']
    frase_classif_norm = normalizar_frase(frase_classif)
    melhor_correspondencia_norm = encontrar_melhor_correspondencia(frase_classif_norm, dataset_mapping)
    
    if not melhor_correspondencia_norm:
        print(f"Não foi encontrada correspondência para a frase: {frase_classif}")
        continue
    
    item_rotulo = dataset_mapping[melhor_correspondencia_norm]
    
    # Exibir as frases correspondentes para verificação
    print(f"\nFrase de classificação: {frase_classif}")
    print(f"Frase correspondente no dataset: {item_rotulo['Frase']}")
    
    palavras = frase_classif.split()
    frases_palavras.append(palavras)
    
    # Atribuir rótulos reais e preditos considerando expressões de múltiplas palavras
    labels_reais = atribuir_rotulos(frase_classif, item_rotulo)
    labels_preditos = atribuir_rotulos(frase_classif, item_classif)
    
    rotulos_reais.extend(labels_reais)
    rotulos_preditos.extend(labels_preditos)

# Avaliar as métricas
labels = list(rotulo_map.values())
relatorio_ajustado = classification_report(
    rotulos_reais,
    rotulos_preditos,
    labels=labels,
    target_names=list(rotulo_map.keys()),
    zero_division=0
)

print(relatorio_ajustado)
