# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os

"""
def scispacy(unified_df, options):
    # Isso tá muito feio, eu sei. Mas nessa estrutura o loop lê cada abstract apenas uma vez, que em teoria é pra ser mais rápido. Quanto ao dicionário, vou formatar ele melhor depois
    nlp = spacy.load("en_ner_bionlp13cg_md")

    dict = {'Gene or gene product': ['GENE_OR_GENE_PRODUCT', [] ], 'Cancer': ['CANCER', [] ], 'Amino acid': ['AMINO_ACID', [] ], 'Organ': ['ORGAN', []], 'Organism': ['ORGANISM', []], 'Simple chemical': ['SIMPLE_CHEMICAL', []]}

    for row in unified_df['Abstract']:
        doc = nlp(row)

        for opt in options:
            data = []
            for entity in doc.ents:
                if entity.label_ == dict[opt][0]:
                    data.append(entity.text)
            dict[opt][1].append(', '.join(set(data)))

    keys = list(dict)
    for n, item in enumerate(dict):
        if dict[item][1]:
            unified_df.insert(10, keys[n], dict[item][1])

    return unified_df
"""


# OLD BUT PRETTY CODE
def genes(unified_df):
    nlp = spacy.load("en_ner_bionlp13cg_md")

    genes_column = []
    for row in unified_df['Abstract']:
        doc = nlp(row)

        genes = []
        for entity in doc.ents:
            if entity.label_ == 'GENE_OR_GENE_PRODUCT' and entity.text:
                genes.append(entity.text)
        genes_column.append(', '.join(set(genes)))

    unified_df.insert(10, 'Genes', genes_column)


    # Filter only genes
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_file_path = os.path.join(script_dir, 'flash_text_model.pickle')
    with open(pickle_file_path, 'rb') as reader:
        kp = pickle.loads(reader.read())

    def process_keywords(text):
        return set(kp.extract_keywords(text))
    
    genes_column = []
    for row in unified_df["Genes"]:
        if not isinstance(row, float):
            genes = process_keywords(row)
            genes_column.append(', '.join(genes))
        else:
            genes_column.append(np.nan)
    unified_df.insert(10, 'flashtext', genes_column)
    unified_df.to_csv('with_flashtext.csv', index=False)

    with open('flash_text_model.pickle', 'rb') as reader:
        kp = pickle.loads(reader.read())

    return unified_df
