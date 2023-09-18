Bambu Systematic Review
==========================

### Step 1:
clone repository `git@github.com:omixlab/bambu-systematic-review.git`
open folder `cd bambu-systematic-review`
### Step 2: 
create env `conda env create`
install scispacy model `pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_ner_bionlp13cg_md-0.5.1.tar.gz`
### Step 3: 
Start redis `redis-server` 
### Step 4: 
Start celery `celery -A src.celery worker --loglevel=info` 
### Step 5: 
Open application in flask `flask --app src run --debugger`

## .env setup is required
.env file example:
```
NCBI_API_KEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
X_ELS_APIKey='YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
X_ELS_Insttoken='ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
FLASHTEXT_MODEL='data/models/flash_text_model.pickle'
```
