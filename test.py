import pandas as pd
from src.utils.unify_dfs import unify

pm = pd.read_csv('/home/gabrielliston/Downloads/pubmed_df.csv')
sc = pd.read_csv('/home/gabrielliston/Downloads/scopus_df.csv')
sd = pd.read_csv('/home/gabrielliston/Downloads/scidir_df.csv')

df = unify(pm, sc, sd)
df.to_csv('/home/gabrielliston/test.csv')

