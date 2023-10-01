# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os

def scispacy_ner(df, entities):
    # NER for entities in abstract
    nlp = spacy.load("en_ner_bionlp13cg_md")

    for selected_entity in entities:
        new_column = []
        for row in df['Abstract'].astype(str):
            doc = nlp(row)

            recognized_list = []
            for entity in doc.ents:
                if entity.label_ == selected_entity and entity.text:
                    recognized_list.append(entity.text)
            new_column.append(', '.join(set(recognized_list)))
            
        df.insert(len(df.columns), f'{selected_entity}', new_column) 
        print(f'Success: NER for {selected_entity} with SciSpacy')
    return df


def flashtext_kp(df, models):
    filtered_column = []

    for selected_model in models:
        pickle_file_path = f"{os.environ.get(f'FLASHTEXT_MODELS')}{selected_model}.pickle"
        with open(pickle_file_path, 'rb') as reader:
            kp = pickle.loads(reader.read())

        # Set column and Run NER if it wasn't selected
        if "genes" in selected_model:
            original_column_label = "GENE_OR_GENE_PRODUCT"
            if "GENE_OR_GENE_PRODUCT" not in df.columns:
                df = scispacy_ner(df, ["GENE_OR_GENE_PRODUCT"])
            else:
                pass

        else:
            original_column_label = "Abstract"
        
        for row in df[original_column_label]:
            filtered_row = []

            if not isinstance(row, float):
                processed_keywords = set(kp.extract_keywords(row))
                filtered_row.append(', '.join(processed_keywords))
            else:
                filtered_row.append(np.nan)

            print(filtered_row)
            filtered_column.append(', '.join(set(filtered_row)))

        new_column_name = selected_model.title().replace("_", " ")
        df.insert(len(df.columns), new_column_name, filtered_column)
    
    print('Success: Keywords proccessed')
    return df