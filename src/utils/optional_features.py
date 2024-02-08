# SCISPACY para identificar genes na abstract
import scispacy
import spacy
import pickle
import numpy as np
import os
from flashtext import KeywordProcessor
from src.models import FlashtextModels


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

        df.insert(len(df.columns), f"{selected_entity}", new_column)
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

    df.insert(len(df.columns), "Filtered Keywords", filtered_column)
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

        df.insert(len(df.columns), model.name, filtered_column)

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
