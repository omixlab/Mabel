Bambu Systematic Review
==========================

### Step 1: 
create env `conda env create -f environment.yml`
### Step 2: 
install models `pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_ner_bionlp13cg_md-0.5.1.tar.gz` 
### Step 3: 
create '.env' file
```
NCBI_API_KEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
X_ELS_APIKey='YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
X_ELS_Insttoken='ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
```
### Step 4: 
Open application in streamlit `streamlit run src/main.py`
