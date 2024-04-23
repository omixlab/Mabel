import json
import os

import numpy as np
import pandas as pd


def unify(job_name, dfs):
    formated_dfs = []

    directory_path = "data/dfs_results/"

    folders = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

    if not folders or "1" not in folders:
        folder = "1"
        os.makedirs(os.path.join(directory_path, folder))
    else:
        highest_numbered_folder = max(folders, key=lambda x: int(x))

        folder = str(int(highest_numbered_folder) + 1)
        os.makedirs(os.path.join(directory_path, folder))

    folder_path = os.path.join(directory_path, folder)

    # PUBMED
    if "pubmed" in dfs:
        pubmed = dfs["pubmed"]

        if pubmed.empty:
            pass
        else:

            # Formatação de alguns elementos
            pm_formated_auth = []
            for row in pubmed["authors"]:
                try:
                    if row != "":
                        authors_list = row.split(";")
                        formated_auth_str = ""
                        for author in authors_list:
                            info = author.split("|")
                            lastname, firstname = info[0], info[1]
                            formated_auth_str += f"{lastname} {firstname}; "
                        pm_formated_auth.append(formated_auth_str)
                    else:
                        pm_formated_auth.append(np.nan)
                except:
                    pm_formated_auth.append("error")

            pm_formated_type = []
            for row in pubmed["publication_types"]:
                try:
                    if ";" in row:
                        type_list = row.split(";")
                        formated_type_str = [
                            "".join(type.split(":", 1)[1:]) for type in type_list
                        ]
                        pm_formated_type.append("; ".join(formated_type_str))

                    else:
                        pm_formated_type.append("".join(row.split(":", 1)[1:]))
                except:
                    pm_formated_type.append("error")

            # Converte em dataframes padronizados
            df = pd.DataFrame(
                    {
                        "Title": pubmed["title"],
                        "DOI": pubmed["doi"],
                        "Abstract": pubmed["abstract"],
                        "Date": pubmed["pubdate"],
                        "Pages": pubmed["pages"],
                        "Journal": pubmed["journal"],
                        "Authors": pm_formated_auth,
                        "Type": pm_formated_type,
                        "Affiliations": pubmed["affiliations"],
                        "MeSH Terms": pubmed["mesh_terms"],
                    }
                )
            df.to_csv(os.path.join(folder_path, f"{job_name}.csv"))
            formated_dfs.append(df)

    # SCOPUS
    if "scopus" in dfs:
        scopus = dfs["scopus"]

        if scopus.empty:
            pass
        else:

            sc_formated_affil = []
            for row in scopus["affiliation"]:
                try:
                    sc_formated_affil.append(
                        "; ".join([entry["affilname"] for entry in row])
                    )
                except:
                    sc_formated_affil.append("error")

            df = pd.DataFrame(
                    {
                        "Title": scopus["dc:title"],
                        "DOI": scopus["prism:doi"],
                        "Abstract": scopus["Abstract"],
                        "Date": scopus["prism:coverDate"],
                        "Pages": scopus["prism:pageRange"],
                        "Journal": scopus["prism:publicationName"],
                        "Authors": scopus["dc:creator"],
                        "Type": scopus["subtypeDescription"],
                        "Affiliations": sc_formated_affil,
                        "MeSH Terms": np.nan,
                    }
                )
            df.to_csv(os.path.join(folder_path, f"{job_name}.csv"))
            formated_dfs.append(df)

    # SCIENCE DIRECT
    if "scidir" in dfs:
        scidir = dfs["scidir"]

        if scidir.empty:
            pass
        else:

            sd_formated_auth = []
            for row in scidir["authors"]:
                try:
                    sd_formated_auth.append(
                        "; ".join([entry["$"] for entry in row["author"]])
                    )
                except:
                    sd_formated_auth.append("error")

            sd_formated_pages = []
            for start, end in zip(
                scidir["prism:startingPage"], scidir["prism:endingPage"]
            ):
                try:
                    sd_formated_pages.append(f"{start}-{end}")
                except:
                    sd_formated_pages.append("error")

            df = pd.DataFrame(
                    {
                        "Title": scidir["dc:title"],
                        "DOI": scidir["prism:doi"],
                        "Abstract": scidir["abstract"],
                        "Date": scidir["prism:coverDate"],
                        "Pages": sd_formated_pages,
                        "Journal": scidir["prism:publicationName"],
                        "Authors": sd_formated_auth,
                        "Type": scidir["pubtype"],
                        "Affiliations": np.nan,
                        "MeSH Terms": np.nan,
                    }
                )
            df.to_csv(os.path.join(folder_path, f"{job_name}.csv"))
            formated_dfs.append(df)

    # SCIELO
    if "scielo" in dfs:
        scielo = dfs["scielo"]

        se_formated_pages = []
        for row1, row2 in zip(scielo["start_page"], scielo["end_page"]):
            if row1 and row2:
                pages = f"{row1}-{row2}"
            else:
                pages = np.nan
            se_formated_pages.append(pages)

        if scielo.empty:
            pass
        else:
            df = pd.DataFrame(
                    {
                        "Title": scielo["title"],
                        "DOI": scielo["doi"],
                        "Abstract": scielo["abstract"],
                        "Date": scielo["year"],
                        "Pages": se_formated_pages,
                        "Journal": scielo["journal"],
                        "Authors": scielo["authors"],
                        "Type": np.nan,
                        "Affiliations": np.nan,
                        "MeSH Terms": np.nan,
                    }
                )
            df.to_csv(os.path.join(folder_path, f"{job_name}.csv"))
            formated_dfs.append(df)


    # PREPRINTS
    if "pprint" in dfs:
        preprints = dfs["pprint"]

        if preprints.empty:
            pass
        else:
            df = pd.DataFrame(
                    {
                        "Title": preprints["title"],
                        "DOI": preprints["doi"],
                        "Abstract": preprints["abstract"],
                        "Date": preprints["date"],
                        "Pages": np.nan,
                        "Journal": preprints["journal"],
                        "Authors": preprints["authors"],
                        "Type": np.nan,
                        "Affiliations": np.nan,
                        "MeSH Terms": np.nan,
                    }
                )
            df.to_csv(os.path.join(folder_path, f"{job_name}.csv"))
            formated_dfs.append(df)


    # Concatenação dos dataframes
    try:
        unified_dataframes = pd.concat(formated_dfs)

        total = len(unified_dataframes)
        unified_dataframes = unified_dataframes.drop_duplicates(subset=['DOI'])
        dropped = len(unified_dataframes)
        print(f"Dropped {total-dropped} duplicates out of {total}")
        print(f"Success: Dataframes unified succesfully ({len(unified_dataframes)} articles in total)")
        return (unified_dataframes)
    except:
        if not formated_dfs:
            print("Error: No results")
        return pd.DataFrame()  # Gera dataframe vazio
