# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os

def genes(unified_df):
    # Find genes or gene products in abstract
    nlp = spacy.load("en_ner_bionlp13cg_md")

    genes_column = []
    for row in unified_df['Abstract'].astype(str):
        doc = nlp(row)

        genes = []
        for entity in doc.ents:
            if entity.label_ == 'GENE_OR_GENE_PRODUCT' and entity.text:
                genes.append(entity.text)
        genes_column.append(', '.join(set(genes)))

    print('Success: read with SciSpacy')


    # Filter only genes

    pickle_file_path =  os.environ.get('FLASHTEXT_MODEL')

    with open(pickle_file_path, 'rb') as reader:
        kp = pickle.loads(reader.read())

    def process_keywords(text):
        return set(kp.extract_keywords(text))
    
    filtered_column = []
    for row in genes_column:
        if not isinstance(row, float):
            genes = process_keywords(row)
            filtered_column.append(', '.join(genes))
        else:
            filtered_column.append(np.nan)

    unified_df.insert(10, 'Genes', filtered_column)
    unified_df.to_csv('/home/gabrielliston/Desktop/with_flashtext.csv', index=False)

    print('Success: genes filtered')
    return unified_df