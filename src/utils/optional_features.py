# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os
from flashtext import KeywordProcessor
from src.models import FlashtextModels
import requests
import json
import time


def scispacy_ner(df, entities):
    # NER for entities in abstract
    nlp = spacy.load("en_ner_bionlp13cg_md")

    for selected_entity in entities:
        new_column = []
        for row in df["Abstract"].astype(str):
            doc = nlp(row)

            recognized_list = []
            for entity in doc.ents:
                if entity.label_ == selected_entity and entity.text:
                    recognized_list.append(entity.text)
            new_column.append(", ".join(set(recognized_list)))

        df.insert(4, f"{selected_entity}", new_column)
        print(f"Success: NER for {selected_entity} with SciSpacy")
    return df


def flashtext_kp_string(df, string):
    keywords = string.split(", ")
    filtered_column = []

    # Write model
    kp = KeywordProcessor(case_sensitive=True)
    kp.add_keywords_from_list(keywords)

    for row in df["Abstract"]:
        filtered_row = []

        if not isinstance(row, float):
            processed_keywords = set(kp.extract_keywords(row))
            filtered_row.append(", ".join(processed_keywords))
        else:
            filtered_row.append(np.nan)

        filtered_column.append(", ".join(set(filtered_row)))

    df.insert(4, "Filtered Keywords", filtered_column)
    print("Success: Keywords processed from string")
    return df


def flashtext_kp(df, models):

    for selected_model in models:
        model = FlashtextModels.query.get(selected_model)
        filtered_column = []

        with open(model.path, "rb") as reader:
            kp = pickle.loads(reader.read())

        # Set column and Run NER if it wasn't selected
        if model.type != None:
            original_column_label = model.type
            if model.type not in df.columns:
                df = scispacy_ner(df, [model.type])

        else:
            original_column_label = "Abstract"

        for row in df[original_column_label]:
            filtered_row = []

            if not isinstance(row, float):
                processed_keywords = set(kp.extract_keywords(row))
                filtered_row.append(", ".join(processed_keywords))
            else:
                filtered_row.append(np.nan)

            filtered_column.append(", ".join(set(filtered_row)))

        df.insert(5, model.name, filtered_column)

    print("Success: Keywords proccessed")
    return df


def flashtext_model_create(name, tsv_file, path):
    # Convert data into gene dict and list
    genes_dict = {}
    genes_list = []

    with open(tsv_file, "r") as file:
        next(file)  # skip head

        for line in file:
            values = line.strip().split("\t")  # Split by tabs

            # gene_id = values[2]
            symbol = values[5]
            aliases = values[6]
            # description = values[7]
            # other_designation = values[8]

            if aliases:
                designations = aliases.split(", ")
                designations.insert(0, symbol)
                genes_dict[symbol] = designations
            else:
                genes_list.append(symbol)

    # Write model
    kp = KeywordProcessor(case_sensitive=True)

    kp.add_keywords_from_dict(genes_dict)
    kp.add_keywords_from_list(genes_list)

    # Save with pickle
    with open(f"./{path}", "wb") as writer:
        writer.write(pickle.dumps(kp))

def pubtator_request(df, entities):
    fail_count = 0
    success_count = 0
    no_pmids_count = 0
    empty_count = 0
    new_columns = {entity_type: [] for entity_type in entities}

    for n, pmid in enumerate(df["PubmedID"]):
        time.sleep(1)
        new_row = {entity_type: [] for entity_type in entities}

        if pmid:
            print(f"{pmid} ({n}/{len(df['PubmedID'])})")
            response = requests.get(f'https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson?pmids={pmid}')
            if response.status_code == 200:
                json_data = response.json()
                for entry in json_data['PubTator3']:
                    for passage in entry['passages']:
                        for annotation in passage['annotations']:
                            print(annotation['infons'])
                            entity_type = annotation['infons']['biotype']

                            if entity_type in entities:
                                if 'name' in annotation['infons']:
                                    name = annotation['infons']['name']
                                    new_row[entity_type].append(name)
                                elif 'text' in annotation['infons']:
                                    name = annotation['infons']['text']
                                    new_row[entity_type].append(name)
                                else:
                                    print('name or text not found')
                                    pass
                
                for entity_type in entities:
                    if new_row[entity_type]:
                        success_count += 1
                        print(new_row[entity_type])
                        new_columns[entity_type].append(', '.join(set(new_row[entity_type])))
                    else:
                        empty_count +=1
                        print("empty")
                        new_columns[entity_type].append(np.nan)
                
            else:
                print('error response')
                fail_count += 1
                for entity_type in entities:
                    new_columns[entity_type].append(np.nan)

        else:
            print('no pmid')
            no_pmids_count += 1
            for entity_type in entities:
                    new_columns[entity_type].append(np.nan)


    print(f"success: {success_count}, fails: {fail_count}, no pmids: {no_pmids_count}, empty: {empty_count}")
    for entity_type in new_columns:
        df.insert(4, f"biotator_{entity_type}", new_columns[entity_type])
    print("Success: Biotator annotation")
    return df