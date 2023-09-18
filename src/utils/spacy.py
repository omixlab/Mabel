# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os

def scispacy_ner(unified_df, entities):
    # NER for entities in abstract
    nlp = spacy.load("en_ner_bionlp13cg_md")

    genes_column = []
    for row in unified_df['Abstract'].astype(str):
        doc = nlp(row)

        genes = []
        for entity in doc.ents:
            if entity.label_ == entities and entity.text:
                genes.append(entity.text)
                print(entity.text)
        genes_column.append(', '.join(set(genes)))
        
    unified_df.insert(10, 'NER', genes_column) 
    print('Success: NER with SciSpacy')
    return unified_df


def only_genes_ner(unified_df, models):
    # NER for entities in abstract
    nlp = spacy.load("en_ner_bionlp13cg_md")

    genes_column = []
    for row in unified_df['Abstract'].astype(str):
        doc = nlp(row)

        genes = []
        for entity in doc.ents:
            if entity.label_ == 'GENE_OR_GENE_PRODUCT' and entity.text:
                genes.append(entity.text)
        genes_column.append(', '.join(set(genes)))

    print('Success: NER with SciSpacy')

    # Filter only genes
    filtered_column = []
    for model in models:
        print(model)
        print(models[model])
        if model:
            print(1)
            pickle_file_path = os.environ.get(f'FLASHTEXT_MODEL_{models[model]}')
            print(pickle_file_path)
            print(2)
            with open(pickle_file_path, 'rb') as reader:
                print(22)
                kp = pickle.loads(reader.read())
            print(3)

            def process_keywords(text):
                return set(kp.extract_keywords(text))
            print(4)
            
            for row in genes_column:
                if not isinstance(row, float):
                    genes = process_keywords(row)
                    filtered_column.append(', '.join(genes))
                else:
                    filtered_column.append(np.nan)

    print(5)
    unified_df.insert(10, 'Genes', filtered_column)
    print('Success: genes filtered')
    return unified_df