Bambu Systematic Review
==========================

### Clone repository 
`git clone git@github.com:omixlab/Mabel.git`

### Open folder 
`cd Mabel`


To run searches, make sure these environment variables are set (see example_env)
```
CELERY_BROKER_URL=XXXXXXXXXXXXXXXXX
CELERY_RESULT_BACKEND=XXXXXXXXXXXXX
SQLALCHEMY_DATABASE_URI=XXXXXXXXXXX
FLASK_SECRET_KEY=XXXXXXXXXXXXXXXXXX

```

### Docker
`make build`
`make run`

Create your account, then log in to the application.
In your profile, set the Elsevier (Scopus, Elsevier) and PubMed tokens.
These can be requested at NCBI [NCBI](https://account.ncbi.nlm.nih.gov/) and Elsevier Developer Portal [Elsevier Developer Portal](https://dev.elsevier.com/).
Elsevier requests are limited; if you need more than 10,000 requests, you can email their development team.

After all tokens are set, you can perform requests in the **Articles Extractor** (Basic or Advanced).  

If you enable the optional feature **Biological Entities**, entities can be extracted using two different methodologies:  
- **SciSpacy + BioSyn** (for normalization)  
- **PubTator** (works only with articles that have PMIDs)

⚠️ Note: BioSyn is trained only for human genes.  
If you want to use other models, you can add a dictionary in TSV format to train the normalizer.


