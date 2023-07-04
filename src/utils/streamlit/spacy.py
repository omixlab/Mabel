# SCISPACY para identificar genes na abstract
import scispacy
import spacy

class Scispacy:
    def __init__(self, unified_df):
        self.unified_df = unified_df

    def genes(self):
        nlp = spacy.load("en_ner_bionlp13cg_md")

        genes_column = []
        for row in self.unified_df['Abstract']:
            doc = nlp(row)

            genes = []
            for entity in doc.ents:
                if entity.label_ == 'GENE_OR_GENE_PRODUCT':
                    genes.append(entity.text)
            genes_column.append(', '.join(set(genes)))

        self.unified_df.insert(10, 'Gene or gene product', genes_column)

        return self.unified_df