import os
import pdb
import pickle
from tqdm import tqdm
import pandas as pd
import ast
from src.biosyn import (
    DictionaryDataset,
    BioSyn,
    TextPreprocess
)

tqdm.pandas()

dictionary_path = 'data/human_genes.tsv'
model_name_or_path = 'pretrained/biosyn-sapbert-bc2gn'

def cache_or_load_dictionary():
    dictionary_name = os.path.splitext(os.path.basename(dictionary_path))[0]
    
    cached_dictionary_path = os.path.join(
        './tmp',
        "cached_{}.pk".format(dictionary_name)
    )

    # If exist, load the cached dictionary
    if os.path.exists(cached_dictionary_path):
        with open(cached_dictionary_path, 'rb') as fin:
            cached_dictionary = pickle.load(fin)
        print("Loaded dictionary from cached file {}".format(cached_dictionary_path))

        dictionary, dict_sparse_embeds, dict_dense_embeds = (
            cached_dictionary['dictionary'],
            cached_dictionary['dict_sparse_embeds'],
            cached_dictionary['dict_dense_embeds'],
        )

    else:
        dictionary = DictionaryDataset(dictionary_path = dictionary_path).data
        dictionary_names = dictionary[:,0]
        dict_sparse_embeds = biosyn.embed_sparse(names=dictionary_names, show_progress=True)
        dict_dense_embeds = biosyn.embed_dense(names=dictionary_names, show_progress=True)
        cached_dictionary = {
            'dictionary': dictionary,
            'dict_sparse_embeds' : dict_sparse_embeds,
            'dict_dense_embeds' : dict_dense_embeds
        }

        if not os.path.exists('./tmp'):
            os.mkdir('./tmp')
        with open(cached_dictionary_path, 'wb') as fin:
            pickle.dump(cached_dictionary, fin)
        print("Saving dictionary into cached file {}".format(cached_dictionary_path))

    return dictionary, dict_sparse_embeds, dict_dense_embeds

def normalize(mention):
    # preprocess mention
    mention = TextPreprocess().run(mention)

    # embed mention
    mention_sparse_embeds = biosyn.embed_sparse(names=[mention])
    mention_dense_embeds = biosyn.embed_dense(names=[mention])

    # calcuate score matrix and get top 1
    sparse_score_matrix = biosyn.get_score_matrix(
        query_embeds=mention_sparse_embeds,
        dict_embeds=dict_sparse_embeds
    )
    dense_score_matrix = biosyn.get_score_matrix(
        query_embeds=mention_dense_embeds,
        dict_embeds=dict_dense_embeds
    )
    sparse_weight = biosyn.get_sparse_weight().item()
    hybrid_score_matrix = sparse_weight * sparse_score_matrix + dense_score_matrix
    hybrid_candidate_idxs = biosyn.retrieve_candidate(
        score_matrix = hybrid_score_matrix, 
        topk = 1
    )
    
    # get predictions from dictionary
    predictions = dictionary[hybrid_candidate_idxs].squeeze(0)
    output = {
        'predictions' : []
    }

    for prediction in predictions:
        predicted_name = prediction[0]
        predicted_id = prediction[1]
        output['predictions'].append({
            'name': predicted_name,
            'id': predicted_id
        })

    return output

# load biosyn model
biosyn = BioSyn(
    use_cuda=True,
    max_length=25
)
    
biosyn.load_model(
    model_name_or_path=model_name_or_path
)

# cache or load dictionary
dictionary, dict_sparse_embeds, dict_dense_embeds = cache_or_load_dictionary()

# Função para processar cada gene e extrair name e id
def process_gene(gene):
    normalized = normalize(gene)
    if normalized and 'predictions' in normalized and len(normalized['predictions']) > 0:
        prediction = normalized['predictions'][0]  # Pega a primeira predição
        return prediction.get('name'), prediction.get('id')
    return gene, None  # Retorna o original se não houver normalização

# Função principal para processar toda a string de genes
def process_gene_column(gene_string):
    if pd.isna(gene_string) or gene_string.strip() == "":
        return None, None

    genes = [g.strip() for g in gene_string.split(',')]
    names = []
    ids = []
    
    for gene in genes:
        name, id_ = process_gene(gene)
        names.append(str(name))
        ids.append(str(id_) if id_ else '')
    
    return ', '.join(names), ', '.join(ids)

df = pd.read_csv('data/human_NLM_GENE_ToNormalize.csv')

# Depois use progress_apply no lugar de apply
df[['GENE_NAMES', 'GENE_IDS']] = df['GENE_OR_GENE_PRODUCT'].progress_apply(
    lambda x: pd.Series(process_gene_column(x))
)

df.to_csv('data/human_NLM_GENE_ToNormalize.csv', index = False)
