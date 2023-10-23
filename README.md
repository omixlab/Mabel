Bambu Systematic Review
==========================

### Clone repository 
`git clone git@github.com:omixlab/bambu-systematic-review.git`

### Open folder 
`cd bambu-systematic-review`

## .env setup is required
Create .env file and fill with your credentials of NCBI and Elsevier
.env file example:
```
NCBI_API_KEY=XXXXXXXXXXXXXXXXXXXXXX
X_ELS_APIKey=XXXXXXXXXXXXXXXXXXXXXX
X_ELS_Insttoken=XXXXXXXXXXXXXXXXXXX
CELERY_BROKER_URL=XXXXXXXXXXXXXXXXX
CELERY_RESULT_BACKEND=XXXXXXXXXXXXX
SQLALCHEMY_DATABASE_URI=XXXXXXXXXXX
FLASK_SECRET_KEY=XXXXXXXXXXXXXXXXXX
FLASHTEXT_MODELS='data/flashtext_models/default_models/'
FLASHTEXT_USER_MODELS='data/flashtext_models/users_models/'
UPLOAD_FILES='data/uploads/'
```
