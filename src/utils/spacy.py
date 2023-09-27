# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os

def scispacy_ner(unified_df, entities):
    # NER for entities in abstract
    nlp = spacy.load("en_ner_bionlp13cg_md")

    for selected_entity in entities:
        new_column = []
        for row in unified_df['Abstract'].astype(str):
            doc = nlp(row)

            recognized_list = []
            for entity in doc.ents:
                if entity.label_ == selected_entity and entity.text:
                    recognized_list.append(entity.text)
            new_column.append(', '.join(set(recognized_list)))
            
        unified_df.insert(len(unified_df.columns), f'{selected_entity}', new_column) 
        print(f'Success: NER for {selected_entity} with SciSpacy')
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
    selected_models = [model.upper() for model in models if models.get(model)]
    print(f'Filtering with {selected_models} models')

    filtered_column = []
    for row in genes_column:
        filtered_row = []
        for model in selected_models:
            pickle_file_path = os.environ.get(f'FLASHTEXT_MODEL_{model}')
            with open(pickle_file_path, 'rb') as reader:
                kp = pickle.loads(reader.read())

            def process_keywords(text):
                return set(kp.extract_keywords(text))
        
            if not isinstance(row, float):
                genes = process_keywords(row)
                filtered_row.append(', '.join(genes))
            else:
                filtered_row.append(np.nan)

        filtered_column.append(', '.join(set(filtered_row)))

    unified_df.insert(10, 'Genes', filtered_column)
    print('Success: genes filtered')
    return unified_df